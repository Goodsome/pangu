from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import override
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.services.ast_visitor import AstVisitor
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    ClassTypeNode,
    CodeNode,
    ExternalNode,
    FunctionNode,
    GenericTypeNode,
    MethodNode,
    ModuleNode,
    ParameterNode,
    TypeVarNode,
    UnionTypeNode,
    VariableNode,
)
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.bin_op import BinOp
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_bin_op import AstBinOp
from codegen.code_metadata.domain.value_objects.ast_call import AstCall
from codegen.code_metadata.domain.value_objects.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_list import AstList
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt_old import (
    AstClassDef,
    AstFunctionDef,
)
from codegen.code_metadata.domain.value_objects.ast_subscript import AstSubscript
from codegen.code_metadata.domain.value_objects.ast_tuple import AstTuple
from codegen.code_metadata.domain.value_objects.ast_type_param import (
    AstTypeParam,
    AstTypeVar,
)
from codegen.code_metadata.domain.value_objects.code_edge import TypedAsEdge
from codegen.code_metadata.infrastructure.gateways.document_context import (
    DocumentContext,
)
from codegen.code_metadata.infrastructure.gateways.traversal_context import (
    TraversalContext,
)
from foundation.common_types.enums import PythonBuiltinType


@dataclass
class EdgeBuilder(AstVisitor):
    module: ModuleNode
    node_registry: NodeRegistry
    document_context: DocumentContext
    context: TraversalContext = field(default_factory=TraversalContext)

    def add_alias_fqn(self, fqn: Fqn, asname: str | None = None):
        node = self.node_registry.get_node(fqn)
        self.add_alias(node, asname=asname)

    def add_alias(self, node: CodeNode, asname: str | None = None):
        self.context.add_alias(node, asname=asname)

    def resolve_alias(self, name: str) -> CodeNode:
        node = self.context.resolve_alias(name)
        if node:
            return node
        if name in PythonBuiltinType._value2member_map_:
            fqn = Fqn(f"std::{name}")
            node = self.node_registry.ensure_external_node(fqn)
            return node
        raise ValueError(f"not found name={name!r}")

    def _find_fqn(self, alias: str) -> Fqn:
        node = self.resolve_alias(alias)
        return node.id

    @property
    def current_node(self) -> CodeNode:
        return self.context.current_node

    def build(self, code_document: CodeDocument):
        with self.context.visit_node(self.module):
            for edge in self.module.outbound_edges:
                if edge.kind is not EdgeType.DEFINES:
                    continue
                self.add_alias_fqn(edge.fqn)
            self.visit(code_document.body)

    @override
    def visit_ast_if(self, node: AstIf):
        is_tc_block = isinstance(node.test, AstName) and node.test.id == "TYPE_CHECKING"
        if is_tc_block:
            self.context.is_type_checking = True
            self.visit(node.body)
            self.context.is_type_checking = False
        else:
            super().visit_ast_if(node)

    @override
    def visit_ast_import(self, node: AstImport):
        for name in node.names:
            self._parse_import_name(
                name.name,
                asname=name.asname,
                is_type_checking=self.context.is_type_checking,
            )

    @override
    def visit_ast_import_from(self, node: AstImportFrom):
        is_type_checking = self.context.is_type_checking
        if node.level > 0:
            relative_level = node.level
            if self.module.is_package:
                relative_level = relative_level - 1
            module_prefix = self.module.get_parent_by_level(relative_level)
        else:
            module_prefix = ""
        module = node.module or ""
        if module_prefix:
            module = module_prefix + "." + module
        if not module:
            raise ValueError(f"ImportFrom module is empty: {node.module}")
        for name in node.names:
            self._parse_import_name(
                name.name,
                from_name=module,
                asname=name.asname,
                is_type_checking=is_type_checking,
            )

    def _parse_import_name(
        self,
        import_name: str,
        from_name: str | None = None,
        asname: str | None = None,
        is_type_checking: bool = False,
    ) -> None:
        if from_name:
            is_external = not from_name.startswith("codegen.")
        else:
            is_external = not import_name.startswith("codegen.")
        if is_external:
            external_fqn = (
                Fqn(f"{from_name}.{import_name}") if from_name else Fqn(import_name)
            )
            node = self.node_registry.get_node(external_fqn)
        else:
            node = self._get_internel_node(import_name=import_name, from_name=from_name)
        if self.module.is_package:
            assert isinstance(node, ClassNode | FunctionNode | VariableNode), (
                f"node={node!r}"
            )
            self.module.exports(node)
        else:
            assert isinstance(
                node, ExternalNode | ClassNode | FunctionNode | VariableNode
            ), f"node={node!r}"
            self.module.imports(node, is_type_checking=is_type_checking, asname=asname)
        self.add_alias(node, asname=asname)

    def _get_internel_node(self, import_name: str, from_name: str | None) -> CodeNode:
        name = import_name
        if from_name is None:
            return self.node_registry.get_node(Fqn(name))
        from_module = self.node_registry.get_node(Fqn(from_name))
        for edge in from_module.outbound_edges:
            if edge.node_name == import_name:
                node = self.node_registry.get_node(edge.fqn)
                return node
        raise ValueError(f"{import_name} not found in {from_name}")

    @override
    def visit_ast_class_def(self, node: AstClassDef):
        class_node = self.document_context.get_node_by_ast(node)
        assert isinstance(class_node, ClassNode)
        with self.context.visit_node(class_node):
            self.add_alias(class_node, asname="self")
            self._visit_class_bases(node.bases)
            self._visit_type_params(node.type_params)
            self.visit(node.decorator_list)
            self.visit(node.body)

    def _visit_class_bases(self, bases: list[AstExpr]):
        for base in bases:
            fqn = self._resolve_expr_to_fqn(base)
            if not fqn:
                continue
            self.current_node.add_edge(EdgeType.INHERITS, fqn=fqn)

    def _visit_type_params(self, type_params: list[AstTypeParam]):
        for type_param in type_params:
            self._visit_type_param(type_param)

    def _visit_type_param(self, type_param: AstTypeParam):
        match type_param:
            case AstTypeVar(name=name, bound=bound):
                context = self.current_node.id.context
                identify = self.current_node.id.identify
                fqn = Fqn(f"{context}::{identify}::{name}")
                type_var_node = TypeVarNode(id=fqn, name=name)
                self.node_registry.add_node(type_var_node)
                self.add_alias(type_var_node)
                self.current_node.add_edge(EdgeType.TYPE_ARGUMENT, fqn)
                with self.context.visit_node(type_var_node):
                    self._resolve_annotation(bound)
            case _:
                raise NotImplementedError(f"type_param={type_param!r}")

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        func_node = self.document_context.get_node_by_ast(node)
        assert isinstance(func_node, (MethodNode, FunctionNode)), func_node
        self._build_overriden_edge(func_node=func_node, ast_node=node)
        with self.context.visit_node(func_node):
            self._visit_arguments(node.arguments)
            with self.context.enter_function():
                self.visit(node.body)
            self._resolve_annotation(node.returns, EdgeType.RETURNS)

    def _build_overriden_edge(
        self, func_node: MethodNode | FunctionNode, ast_node: AstFunctionDef
    ):
        if not isinstance(func_node, MethodNode):
            return
        if not ast_node.is_override:
            return
        class_node = self.context.current_node
        assert isinstance(class_node, ClassNode), class_node
        for edge in class_node.get_inherits_edges():
            target_fqn = Fqn(f"{edge.fqn}::{func_node.name}")
            func_node.overrides(target_fqn=target_fqn)

    def _visit_arguments(self, arguments: list[AstAssign | AstAnnAssign]):
        for arg in arguments:
            parameter_node = self.document_context.get_node_by_ast(arg)
            self.add_alias(parameter_node)
            if isinstance(arg, AstAnnAssign) and isinstance(arg.target, AstName):
                with self.context.visit_node(parameter_node):
                    self._resolve_annotation(arg.annotation)
            self.visit(arg)

    @override
    def visit_ast_assign(self, node: AstAssign):
        target = node.target
        if isinstance(target, AstName) and (not self.context.in_function_body):
            fqn = Fqn(f"{self.current_node.id}::{target.id}")
            variable_node = self.node_registry.get_node(fqn)
            with self.context.visit_node(variable_node):
                self._visit_annotated_value(node.value)
        else:
            super().visit_ast_assign(node)

    def _visit_annotated_value(self, node: AstExpr | None):
        match node:
            case AstSubscript(value=AstName(id="Annotated"), slice=AstTuple(elts=elts)):
                self._resolve_annotation(elts[0])
                self.visit(elts[:1])
            case _:
                self.visit(node)

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        target = node.target
        if isinstance(target, AstName) and (not self.context.in_function_body):
            fqn = Fqn(f"{self.current_node.id}::{target.id}")
            variable_node = self.node_registry.get_node(fqn)
            with self.context.visit_node(variable_node):
                self._resolve_annotation(node.annotation)
                self.visit(node.value)
        else:
            super().visit_ast_ann_assign(node)

    @override
    def visit_ast_attribute(self, node: AstAttribute):
        fqn = self._resolve_expr_to_fqn(node)
        if fqn:
            self.current_node.add_edge(EdgeType.READS, fqn)
        self.visit(node.value)

    @override
    def visit_ast_call(self, node: AstCall):
        fqn = self._resolve_expr_to_fqn(node.func)
        if fqn:
            self.current_node.add_edge(EdgeType.CALLS, fqn)
        self.visit(node.func)
        self.visit(node.args)
        self.visit(node.kwargs)

    def _resolve_expr_to_fqn(self, node: AstExpr | None) -> Fqn | None:
        match node:
            case AstName(id=name):
                try:
                    return self._find_fqn(name)
                except:
                    return
            case AstAttribute(value=value, attr=attr):
                base_fqn = self._resolve_expr_to_fqn(value)
                if not base_fqn:
                    return None
                base_node = self.node_registry.find_node(base_fqn)
                if base_node is None:
                    return Fqn(f"{base_fqn}::{attr}")
                match base_node:
                    case ModuleNode() | ClassNode() | ExternalNode():
                        return Fqn(f"{base_fqn}::{attr}")
                    case VariableNode() | ParameterNode():
                        edge = base_node.typed_as_edge
                        base_fqn = self._resolve_typed_as_edge(edge)
                        if base_fqn is None:
                            return None
                        return Fqn(f"{base_fqn}::{attr}")
                    case _:
                        return None
            case _:
                return

    def _resolve_typed_as_edge(self, edge: TypedAsEdge | None) -> Fqn | None:
        if edge is None:
            return None
        type_node = self.node_registry.get_node(edge.fqn)
        match type_node:
            case ClassTypeNode():
                return type_node.references_edge.fqn
            case GenericTypeNode():
                return
            case UnionTypeNode():
                return
            case _:
                raise NotImplementedError(f"type_node={type_node!r}")

    def _resolve_expr_to_fqns(self, node: AstExpr) -> Iterable[Fqn]:
        match node:
            case AstName(id=id):
                yield self._find_fqn(id)
            case AstBinOp(left=left, op=BinOp.BIT_OR, right=right):
                yield from self._resolve_expr_to_fqns(left)
                yield from self._resolve_expr_to_fqns(right)
            case _:
                pass

    def _resolve_annotation(
        self, annotation: AstExpr | None, edge_type: EdgeType = EdgeType.TYPED_AS
    ):
        if annotation is None:
            return
        match annotation:
            case AstName(id=name):
                node = self._get_class_type_node(name)
            case AstConstant(value=None):
                node = self._get_class_type_node("None")
            case AstBinOp(op=BinOp.BIT_OR):
                node = self._get_union_type_node(annotation)
            case AstSubscript(value=AstName(id="Annotated"), slice=AstTuple(elts=elts)):
                self._resolve_annotation(elts[0], edge_type=edge_type)
                self.visit(elts[:1])
                return
            case AstSubscript(value=value, slice=slice):
                node = self._resolve_ast_subscript(value, slice)
            case AstAttribute():
                node = self._get_attribute_type_node(annotation)
            case _:
                raise NotImplementedError(
                    f"annotation={annotation!r}, self.current_node.id={self.current_node.id!r}"
                )
        self.current_node.add_edge(edge_type, node.id)

    def _collect_class_types(
        self, ast_expr: AstExpr
    ) -> Iterable[ClassTypeNode | GenericTypeNode]:
        match ast_expr:
            case AstName(id=name):
                yield self._get_class_type_node(name)
            case AstConstant(value=None):
                yield self._get_class_type_node("None")
            case AstBinOp(left=left, op=BinOp.BIT_OR, right=right):
                yield from self._collect_class_types(left)
                yield from self._collect_class_types(right)
            case AstSubscript(value=value, slice=slice):
                yield self._resolve_ast_subscript(value, slice)
            case AstAttribute():
                yield self._get_attribute_type_node(ast_expr)
            case _:
                raise NotImplementedError(f"ast_expr={ast_expr!r}")

    def _collect_type_nodes(
        self, ast_expr: AstExpr
    ) -> Iterable[ClassTypeNode | UnionTypeNode | GenericTypeNode]:
        match ast_expr:
            case AstName(id=name):
                yield self._get_class_type_node(name)
            case AstConstant(value=None):
                yield self._get_class_type_node(PythonBuiltinType.NONE)
            case AstConstant(value=Ellipsis):
                yield self._get_class_type_node(PythonBuiltinType.ELLIPSIS)
            case AstBinOp(op=BinOp.BIT_OR):
                yield self._get_union_type_node(ast_expr)
            case AstSubscript(value=value, slice=slice):
                yield self._resolve_ast_subscript(value, slice)
            case AstTuple(elts=elts):
                for elt in elts:
                    yield from self._collect_type_nodes(elt)
            case AstAttribute():
                yield self._get_attribute_type_node(ast_expr)
            case _:
                raise NotImplementedError(
                    f"ast_expr={ast_expr!r}, self.current_node.id={self.current_node.id!r}"
                )

    def _get_attribute_type_node(self, attribute: AstAttribute) -> ClassTypeNode:
        reference_fqn = self._resolve_expr_to_fqn(attribute)
        if reference_fqn is None:
            raise NotImplementedError(f"attribute={attribute!r}")
        assert "::" in reference_fqn, reference_fqn
        context = reference_fqn.parts[0]
        parts = reference_fqn.split("::")[1:]
        parts[0] = f"{context}::{parts[0]}"
        fqn = Fqn(".".join((f"<{p}>" for p in parts)))
        existing = self.node_registry.find_node(fqn)
        if existing:
            assert isinstance(existing, ClassTypeNode), existing
            return existing
        node = ClassTypeNode(id=fqn, name=fqn.symbol)
        node.add_edge(EdgeType.REFERENCES, reference_fqn)
        self.node_registry.add_node(node)
        return node

    def _get_class_type_node(self, reference_name: str) -> ClassTypeNode:
        reference_fqn = self._find_fqn(reference_name)
        context = reference_fqn.context
        if "::" in reference_fqn:
            parts = reference_fqn.split("::")[1:]
            parts[0] = f"{context}::{parts[0]}"
            fqn = Fqn(".".join((f"<{p}>" for p in parts)))
        else:
            fqn = Fqn(f"<{context}::{reference_fqn.symbol}>")
        existing = self.node_registry.find_node(fqn)
        if existing:
            assert isinstance(existing, ClassTypeNode), existing
            return existing
        node = ClassTypeNode(id=fqn, name=reference_name)
        node.add_edge(EdgeType.REFERENCES, reference_fqn)
        self.node_registry.add_node(node)
        return node

    def _get_union_type_node(self, ast_bin_op: AstBinOp) -> UnionTypeNode:
        class_type_nodes = list(self._collect_class_types(ast_bin_op))
        fqn = Fqn("|".join((n.id for n in class_type_nodes)))
        name = "|".join((n.name for n in class_type_nodes))
        if len(name) >= 100:
            name = name[:100] + "..."
        existing = self.node_registry.find_node(fqn)
        if existing:
            assert isinstance(existing, UnionTypeNode), existing
            return existing
        node = UnionTypeNode(id=fqn, name=name)
        for class_type_node in class_type_nodes:
            node.add_edge(EdgeType.UNION_MEMBER, fqn=class_type_node.id)
        self.node_registry.add_node(node)
        return node

    def _resolve_ast_subscript(self, value: AstExpr, slice: AstExpr) -> GenericTypeNode:
        match value:
            case AstName():
                base_type = self._get_class_type_node(value.id)
            case AstAttribute():
                base_type = self._get_attribute_type_node(value)
            case _:
                raise NotImplementedError(f"value={value!r}")
        slices = list(self._collect_type_nodes(slice))
        fqn = Fqn(f"{base_type.id}[{','.join((s.id for s in slices))}]")
        name = f"{base_type.name}[{','.join((s.name for s in slices))}]"
        existing = self.node_registry.find_node(fqn)
        if existing:
            assert isinstance(existing, GenericTypeNode), existing
            return existing
        node = GenericTypeNode(id=fqn, name=name)
        node.add_edge(EdgeType.BASE_TYPE, fqn=base_type.id)
        for n in slices:
            node.add_edge(EdgeType.TYPE_ARGUMENT, n.id)
        self.node_registry.add_node(node)
        return node
