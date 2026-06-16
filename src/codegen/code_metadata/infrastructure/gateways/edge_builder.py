from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import override

from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.services.ast_visitor import AstVisitor
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_edge import CodeEdgeAggregate
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    CodeNode,
    ExternalNode,
    FunctionNode,
    MethodNode,
    ModuleNode,
    ParameterNode,
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
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_subscript import AstSubscript
from codegen.code_metadata.domain.value_objects.ast_tuple import AstTuple
from codegen.code_metadata.infrastructure.gateways.traversal_context import (
    TraversalContext,
)
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class EdgeBuilder(AstVisitor):
    module: ModuleNode
    node_registry: NodeRegistry
    local_aliases: dict[str, Fqn] = field(init=False)
    context: TraversalContext = field(default_factory=TraversalContext)

    function_local_aliases: dict[str, Fqn] = field(default_factory=dict)

    def __post_init__(self):
        self.local_aliases = {}
        for edge in self.module.outbound_edges:
            if edge.kind is not EdgeType.DEFINES:
                continue
            target_name = edge.fqn.split("::")[-1]
            self.local_aliases[target_name] = edge.fqn

    @property
    def current_node(self) -> CodeNode:
        return self.context.current_node

    def build(self, code_document: CodeDocument):
        self.context.stack_node(self.module)
        self.visit(code_document.body)
        self.context.pop_node()

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
            external_fqn = f"{from_name}.{import_name}" if from_name else import_name
            node = self.node_registry.get_node(external_fqn)
        else:
            node = self._get_internel_node(import_name=import_name, from_name=from_name)
        if self.module.is_package:
            assert isinstance(
                node, ClassNode | FunctionNode | VariableNode
            ), f"{node=}"
            self.module.exports(
                node
            )
        else:
            assert isinstance(
                node, ExternalNode | ClassNode | FunctionNode | VariableNode
            ), f"{node=}"
            self.module.imports(
                node,
                is_type_checking=is_type_checking,
                asname=asname,
            )
        if asname:
            local_alias_key = asname
        else:
            local_alias_key = node.name
        self.local_aliases[local_alias_key] = node.id

    def _get_internel_node(self, import_name: str, from_name: str | None) -> CodeNode:
        name = import_name
        if from_name is None:
            return self.node_registry.get_node(name)
        from_module = self.node_registry.get_node(from_name)
        for edge in from_module.outbound_edges:
            if edge.node_name == import_name:
                node = self.node_registry.get_node(edge.fqn)
                return node
        raise ValueError(f"{import_name} not found in {from_name}")

    @override
    def visit_ast_class_def(self, node: AstClassDef):

        class_fqn = Fqn(f"{self.context.current_node.id}::{node.name}")
        class_node = self.node_registry.get_node(class_fqn)
        assert isinstance(class_node, ClassNode)

        self.local_aliases["self"] = class_fqn

        with self.context.visit_node(class_node):
            self._visit_class_bases(node.bases)
            self.visit(node.decorator_list)
            self.visit(node.body)

        self.local_aliases.pop("self")

    def _visit_class_bases(self, bases: list[AstExpr]):
        for base in bases:
            fqn = self._resolve_expr_to_fqn(base)
            if not fqn:
                continue
            self.current_node.add_edge(EdgeType.INHERITS, fqn=fqn)

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        func_fqn = f"{self.context.current_node.id}::{node.name}"
        if node.is_overload:
            func_fqn = f"{func_fqn}<overload_{node.lineno}>"
        elif node.is_setter_property:
            func_fqn = f"{func_fqn}<setter>"
        elif node.is_deleter_property:
            func_fqn = f"{func_fqn}<deleter>"
        elif node.is_expression_property:
            func_fqn = f"{func_fqn}<expression>"
        func_node = self.node_registry.get_node(func_fqn)
        assert isinstance(func_node, (MethodNode, FunctionNode)), func_node

        self._build_overriden_edge(func_node=func_node, ast_node=node)
        with self.context.visit_node(func_node):
            self._visit_arguments(node.arguments)
            with self.context.enter_function():
                self.visit(node.body)
            self._visit_return(node.returns)

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
            func_node.overrides(
                target_fqn=target_fqn,
            )

    def _find_fqn(self, alias: str) -> Fqn:
        if alias in self.function_local_aliases:
            return self.function_local_aliases[alias]
        if alias in self.local_aliases:
            return self.local_aliases[alias]
        return Fqn(alias)

    def _visit_arguments(self, arguments: list[AstAssign | AstAnnAssign]):
        self.function_local_aliases = {}
        for arg in arguments:
            if isinstance(arg, AstAnnAssign) and isinstance(arg.target, AstName):
                target_fqn = self._resolve_expr_to_fqn(arg.annotation)
                if target_fqn:
                    self.function_local_aliases[arg.target.id] = target_fqn
            self.visit(arg)

    def _visit_return(self, returns: AstExpr | None):
        fqn = self._resolve_expr_to_fqn(returns)
        if fqn:
            self.current_node.add_edge(EdgeType.RETURNS, fqn)
        self.visit(returns)

    @override
    def visit_ast_assign(self, node: AstAssign):
        target = node.target
        if isinstance(target, AstName) and not self.context.in_function_body:
            fqn = f"{self.current_node.id}::{target.id}"
            variable_node = self.node_registry.get_node(fqn)
            with self.context.visit_node(variable_node):
                self._visit_annotated_value(node.value)
        else:
            super().visit_ast_assign(node)

    def _visit_annotated_value(self, node: AstExpr | None):
        match node:
            case AstSubscript(value=AstName(id="Annotated"), slice=AstTuple(elts=elts)):
                for fqn in self._resolve_expr_to_fqns(elts[0]):
                    self.current_node.add_edge(EdgeType.TYPED_AS, fqn)
                self.visit(elts[:1])
            case _:
                self.visit(node)

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        target = node.target
        if isinstance(target, AstName) and not self.context.in_function_body:
            fqn = f"{self.current_node.id}::{target.id}"
            variable_node = self.node_registry.get_node(fqn)
            with self.context.visit_node(variable_node):
                fqn = self._resolve_expr_to_fqn(node.annotation)
                if fqn:
                    self.current_node.add_edge(EdgeType.TYPED_AS, fqn)
                self.visit(node.annotation)
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
    def visit_ast_name(self, node: AstName):
        return
        
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
                return self._find_fqn(name)
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
                        for edge in base_node.outbound_edges:
                            if edge.kind == EdgeType.TYPED_AS:
                                return Fqn(f"{edge.fqn}::{attr}")
                    case _:
                        # raise NotImplementedError(f"{base_fqn=}, {self.current_node.id=}")
                        return None
            case _:
                return
                # raise NotImplementedError(f"{node=}")

    def _resolve_expr_to_fqns(self, node: AstExpr) -> Iterable[Fqn]:
        match node:
            case AstName(id=id):
                yield self._find_fqn(id)
            case AstBinOp(left=left, op=BinOp.BIT_OR, right=right):
                yield from self._resolve_expr_to_fqns(left)
                yield from self._resolve_expr_to_fqns(right)
            case _:
                pass