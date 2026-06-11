from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import override
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
)
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import FunctionNode
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.value_objects.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.infrastructure.gateways.module_build_context import (
    ModuleBuildContext,
)
from codegen.code_metadata.infrastructure.gateways.utils import get_import_from_module


@dataclass
class FileSystemCodeGraphBuilder(CodeGraphBuilder):
    """从文件系统构建 CodeNode 图的实现。"""

    get_project_documents: GetProjectDocumentsHandler

    @override
    def get_code_documents(self, module_path: Path) -> list[CodeDocument]:
        query = GetProjectDocumentsQuery(dir_path=module_path)
        result = self.get_project_documents.handle(query)
        return result.code_documents

    @override
    def build_nodes(
        self,
        root_path: Path,
        node_registry: NodeRegistry,
        code_documents: list[CodeDocument],
    ) -> set[str]:
        acl = CodeGraphAcl(
            root_path=root_path, fqn_factory=FqnFactory(), node_registery=node_registry
        )
        acl.build_nodes(code_documents)
        return acl.imports

    @override
    def build_edges(
        self, node_registry: NodeRegistry, code_documents: list[CodeDocument]
    ) -> None:
        fqn_factory = FqnFactory()
        for code_document in code_documents:
            if not code_document.is_init_file:
                continue
            module_fqn = fqn_factory.build_module_fqn(code_document.physical_path)
            module = node_registry.get_node(module_fqn)
            assert isinstance(module, ModuleNode)
            module_builder = ModuleBuildContext(module, code_document, node_registry)
            module_builder.build()
        for code_document in code_documents:
            if code_document.is_init_file:
                continue
            module_fqn = fqn_factory.build_module_fqn(code_document.physical_path)
            module = node_registry.get_node(module_fqn)
            assert isinstance(module, ModuleNode)
            module_builder = ModuleBuildContext(module, code_document, node_registry)
            module_builder.build()


@dataclass
class CodeGraphAcl:
    root_path: Path
    fqn_factory: FqnFactory
    node_registery: NodeRegistry
    imports: set[str] = field(default_factory=set)

    def build_nodes(self, code_documents: list[CodeDocument]) -> None:
        for doc in code_documents:
            self._build_module_node(doc)

    def _add_node(self, dto: CodeNode) -> None:
        self.node_registery.add_node(dto)

    def _build_module_by_path(self, path: Path) -> ModuleNode:
        module_fqn = self.fqn_factory.build_module_fqn(path)
        node = ModuleNode(id=module_fqn, name=module_fqn.rsplit(".", maxsplit=1)[-1])
        self._add_node(node)
        return node

    def _find_or_create_module(self, path: Path) -> ModuleNode:
        module_fqn = self.fqn_factory.build_module_fqn(path)
        node = self.node_registery.find_node(module_fqn)
        if node:
            assert isinstance(node, ModuleNode)
            return node
        node = self._build_module_by_path(path)
        return node

    def _ensure_parent_module(self, module: ModuleNode) -> None:
        module_path = module.get_physical_path()
        if module_path.with_suffix("") == self.root_path:
            return
        assert len(module_path.parts) >= len(
            self.root_path.parts
        ), f"module_path={module_path!r} not under self.root_path={self.root_path!r}"
        parent_path = module_path.parent
        parent = self._find_or_create_module(parent_path)
        parent.is_package = True
        parent.contains(module)

    def _build_module_node(self, code_document: CodeDocument) -> ModuleNode:
        path = code_document.physical_path
        node = self._find_or_create_module(path)
        node.description = code_document.description
        node.is_package = path.name == "__init__.py"
        self._ensure_parent_module(node)
        for stmt in code_document.body:
            self._parse_stmt(stmt, node)
        return node

    def _parse_stmt(self, stmt: AstStmt, parent_node: ModuleNode | ClassNode) -> None:
        match stmt:
            case AstClassDef():
                assert isinstance(
                    parent_node, ModuleNode
                ), "parent node need to be module"
                self._parse_class_def(stmt, parent_node)
            case AstFunctionDef():
                self._parse_function_def(stmt, parent_node)
            case AstAssign() | AstAnnAssign():
                self._parse_assign(stmt, parent_node)
            case (
                AstImport() | AstImportFrom() | AstIf(test=AstName(id="TYPE_CHECKING"))
            ):
                assert isinstance(
                    parent_node, ModuleNode
                ), "parent node need to be module"
                self._parse_ast_imports(stmt, parent_node)
            case AstExprStmt(value=AstConstant()):
                pass
            case AstExprStmt():
                self._parse_expr(stmt, parent_node)
            case AstPass():
                pass
            case AstIf():
                pass
            case _:
                raise NotImplementedError(
                    f"Unsupported statement: stmt={stmt!r} in parent_node.fqn={parent_node.id!r}"
                )

    def _parse_ast_imports(self, stmt: AstStmt, node: ModuleNode):
        match stmt:
            case AstImport(names=names):
                for name in names:
                    self.imports.add(name.name)
            case AstImportFrom(module=module, level=level):
                from_module = get_import_from_module(
                    origin_module=module, level=level, module_node=node
                )
                self.imports.add(from_module)
            case AstIf(test=AstName(id="TYPE_CHECKING"), body=body):
                for b in body:
                    self._parse_ast_imports(b, node)
            case _:
                pass

    def _parse_expr(self, stmt: AstExprStmt, node: ModuleNode | ClassNode):
        if isinstance(node, ClassNode):
            raise NotImplementedError(f"stmt={stmt!r}, node={node!r}")
        node.exprs.append(stmt.value)

    def _parse_class_def(
        self, class_def: AstClassDef, module_node: ModuleNode
    ) -> ClassNode:
        class_fqn = f"{module_node.id}::{class_def.name}"
        node = ClassNode(
            id=class_fqn,
            name=class_def.name,
            description=class_def.description,
            decorator_list=class_def.decorator_list,
            bases=class_def.bases,
            type_params=class_def.type_params,
        )
        module_node.defines(node)
        for stmt in class_def.body:
            self._parse_stmt(stmt, node)
        self._add_node(node)
        return node

    def _parse_function_def(
        self, func_def: AstFunctionDef, parent_node: ModuleNode | ClassNode
    ) -> FunctionNode | MethodNode:
        func_fqn = f"{parent_node.id}::{func_def.name}"
        if func_def.is_overload:
            func_fqn = f"{func_fqn}<overload_{func_def.lineno}>"
        elif func_def.is_setter_property:
            func_fqn = f"{func_fqn}<setter>"
        elif func_def.is_deleter_property:
            func_fqn = f"{func_fqn}<deleter>"
        elif func_def.is_expression_property:
            func_fqn = f"{func_fqn}<expression>"
        match parent_node:
            case ClassNode():
                func_node = MethodNode(
                    id=func_fqn,
                    name=func_def.name,
                    decorator_list=func_def.decorator_list,
                    returns=func_def.returns,
                    body=func_def.body,
                )
                parent_node.defines(func_node)
            case ModuleNode():
                func_node = FunctionNode(
                    id=func_fqn,
                    name=func_def.name,
                    decorator_list=func_def.decorator_list,
                    returns=func_def.returns,
                    body=func_def.body,
                )
                parent_node.defines(func_node)
        self._add_node(func_node)
        for arg in func_def.arguments:
            self._parse_assign(arg, func_node)
        return func_node

    def _parse_assign(
        self,
        assign: AstAssign | AstAnnAssign,
        parent_node: ModuleNode | ClassNode | MethodNode | FunctionNode,
    ) -> None:
        target = assign.target
        if not isinstance(target, AstName):
            return
        self._create_variable_node(
            name=target.id,
            parent_node=parent_node,
            annotation=assign.annotation,
            value=assign.value,
        )

    def _create_variable_node(
        self,
        name: str,
        parent_node: ModuleNode | ClassNode | FunctionNode | MethodNode,
        annotation: AstExpr | None = None,
        value: AstExpr | None = None,
    ) -> VariableNode:
        var_fqn = f"{parent_node.id}::{name}"
        node = VariableNode(id=var_fqn, name=name, annotation=annotation, value=value)
        parent_node.defines(node)
        self._add_node(node)
        return node
