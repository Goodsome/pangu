from dataclasses import dataclass
from typing import override
from code_dom.application.queries.get_code_document_diff import (
    GetCodeDocumentDiffHandler,
)
from code_dom.application.queries.get_code_document_diff import GetCodeDocumentDiffQuery
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.ports.file_differ import FileDiffer
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import FunctionNode
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.code_node import ParameterNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.value_objects.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_list import AstList
from codegen.code_metadata.domain.value_objects.ast_alias import AstAlias
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstStmt
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge
from codegen.code_metadata.domain.value_objects.code_edge import ContainsEdge
from codegen.code_metadata.domain.value_objects.code_edge import DefinesEdge
from codegen.code_metadata.domain.value_objects.code_edge import ExportsEdge
from codegen.code_metadata.domain.value_objects.code_edge import ImportsEdge
from codegen.code_metadata.domain.value_objects.code_edge import InheritsEdge
from codegen.code_metadata.domain.value_objects.code_edge import ReadsEdge


@dataclass
class FileSystemFileDiffer(FileDiffer):
    handler: GetCodeDocumentDiffHandler

    @override
    def get_diff_metric(
        self, module: ModuleNode, node_registry: NodeRegistry
    ) -> FileMetrics:
        code_document = module_node_dto_to_code_document(module, node_registry)
        query = GetCodeDocumentDiffQuery(code_document=code_document)
        file_metrics = self.handler.execute(query=query)
        return file_metrics


def module_node_dto_to_code_document(
    module: ModuleNode, node_registry: NodeRegistry
) -> CodeDocument:
    if module.is_package:
        return build_package_dom(module)
    else:
        return build_file_dom(module=module, node_registry=node_registry)


def build_file_dom(module: ModuleNode, node_registry: NodeRegistry) -> CodeDocument:
    physical_path = FqnFactory.fqn_to_path(module.id).with_suffix(".py")
    imports: list[AstStmt] = []
    if_imports: list[AstStmt] = []
    body: list[AstStmt] = []
    for edge in module.outbound_edges:
        match edge:
            case ContainsEdge() | InheritsEdge() | ReadsEdge():
                continue
            case ImportsEdge(is_type_checking=True):
                if_imports.append(edge_to_ast_stmt(edge, node_registry))
            case ImportsEdge(is_type_checking=False):
                imports.append(edge_to_ast_stmt(edge, node_registry))
            case _:
                body.append(edge_to_ast_stmt(edge, node_registry))
    for expr in module.exprs:
        body.append(AstExprStmt(value=expr))
    if if_imports:
        imports.append(AstIf(test=AstName(id="TYPE_CHECKING"), body=if_imports))
    return CodeDocument(
        physical_path=physical_path, body=imports + body, description=module.description
    )


def build_package_dom(module: ModuleNode) -> CodeDocument:
    physical_path = FqnFactory.fqn_to_path(module.id) / "__init__.py"
    body: list[AstStmt] = []
    all_values: list[AstExpr] = []
    for edge in module.outbound_edges:
        match edge:
            case ExportsEdge(fqn=fqn):
                node_name = fqn.symbol
                constant = AstConstant(value=node_name)
                all_values.append(constant)
                import_from = AstImportFrom(
                    module=fqn.module_fqn, names=[AstAlias(name=node_name)]
                )
                body.append(import_from)
            case _:
                pass
    if all_values:
        body.append(
            AstAssign(targets=[AstName(id="__all__")], value=AstList(elts=all_values))
        )
    for expr in module.exprs:
        body.append(AstExprStmt(value=expr))
    return CodeDocument(
        physical_path=physical_path, body=body, description=module.description
    )


def edge_to_ast_stmt(edge: CodeEdge, node_registry: NodeRegistry) -> AstStmt:
    match edge:
        case ImportsEdge():
            return imports_edge_to_ast(edge, node_registry)
        case DefinesEdge():
            return contains_edge_to_ast(edge, node_registry)
        case _:
            raise NotImplementedError(f"edge={edge!r}")


def node_to_ast_stmt(node: CodeNode, node_registry: NodeRegistry) -> AstStmt:
    match node:
        case ClassNode():
            return class_node_dto_to_ast_class_def(node, node_registry)
        case MethodNode() | FunctionNode():
            return method_node_dto_to_ast(node, node_registry)
        case VariableNode() | ParameterNode():
            return variable_node_dto_to_ast(node, node_registry)
        case _:
            raise NotImplementedError(f"node.kind={node.kind!r}, node.fqn={node.id!r}")


def class_node_dto_to_ast_class_def(
    class_node: ClassNode, node_registry: NodeRegistry
) -> AstClassDef:
    body: list[AstStmt] = []
    for edge in class_node.outbound_edges:
        match edge:
            case InheritsEdge() | ReadsEdge():
                continue
            case _:
                body.append(edge_to_ast_stmt(edge, node_registry))
    if not body:
        body = [AstPass()]
    return AstClassDef(
        name=class_node.name,
        description=class_node.description,
        bases=class_node.bases,
        keywords=[],
        body=body,
        decorator_list=class_node.decorator_list,
        type_params=class_node.type_params,
    )


def method_node_dto_to_ast(
    method_node: MethodNode | FunctionNode, node_registry: NodeRegistry
) -> AstFunctionDef:
    arguments = collect_arguments_from_outbound_edges(
        method_node.outbound_edges, node_registry
    )
    body = method_node.body
    if not body:
        body = [AstPass()]
    return AstFunctionDef(
        name=method_node.name,
        body=method_node.body,
        decorator_list=method_node.decorator_list,
        lineno=0,
        arguments=arguments,
        returns=method_node.returns,
        is_async=method_node.is_async,
    )


def variable_node_dto_to_ast(
    variable_node: VariableNode | ParameterNode, node_registry: NodeRegistry
) -> AstAssign | AstAnnAssign:
    target = AstName(id=variable_node.name)
    if variable_node.annotation:
        return AstAnnAssign(
            target=target,
            annotation=variable_node.annotation,
            value=variable_node.value,
        )
    return AstAssign(targets=[target], value=variable_node.value)


def contains_edge_to_ast(edge: DefinesEdge, node_registry: NodeRegistry) -> AstStmt:
    target_node = node_registry.get_node(edge.fqn)
    ast_stmt = node_to_ast_stmt(target_node, node_registry)
    return ast_stmt


def imports_edge_to_ast(
    edge: ImportsEdge, node_registry: NodeRegistry
) -> AstImport | AstImportFrom:
    if "::" in edge.fqn:
        module, name = edge.fqn.rsplit("::", 1)
        imports = AstImportFrom(
            module=module, names=[AstAlias(name=name, asname=edge.asname)]
        )
    elif "." in edge.fqn:
        module, name = edge.fqn.rsplit(".", 1)
        imports = AstImportFrom(
            module=module, names=[AstAlias(name=name, asname=edge.asname)]
        )
    else:
        imports = AstImport(names=[AstAlias(name=edge.fqn, asname=edge.asname)])
    return imports


def collect_arguments_from_outbound_edges(
    edges: list[CodeEdge], node_registry: NodeRegistry
) -> list[AstAssign | AstAnnAssign]:
    arguments: list[AstAssign | AstAnnAssign] = []
    for edge in edges:
        if edge.kind is not EdgeType.DEFINES:
            continue
        target_node = node_registry.get_node(edge.fqn)
        if not isinstance(target_node, ParameterNode):
            continue
        ast_arg = variable_node_dto_to_ast(target_node, node_registry)
        arguments.append(ast_arg)
    return arguments
