from codegen.shared.domain.enums import PythonBuiltinType
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from dataclasses import dataclass, field
from typing import override

from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.services.ast_visitor import AstVisitor
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    CodeNode,
    ExternalNode,
    FunctionNode,
    MethodNode,
    ModuleNode,
    VariableNode,
)
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.infrastructure.gateways.traversal_context import (
    TraversalContext,
)


@dataclass
class EdgeBuilder(AstVisitor):
    module: ModuleNode
    node_registry: NodeRegistry
    local_aliases: dict[str, str] = field(init=False)
    context: TraversalContext = field(default_factory=TraversalContext)
    
    function_local_aliases: dict[str, str] = field(default_factory=dict)

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
    
    @property
    def current_edge(self) -> EdgeType | None:
        return self.context.current_edge
    
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
        assert isinstance(node, ExternalNode | ClassNode | FunctionNode | VariableNode), f"{node=}"
        self.module.imports(node, is_type_checking=is_type_checking, asname=asname)
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
        
        class_fqn = f"{self.context.current_node.id}::{node.name}"
        class_node = self.node_registry.get_node(class_fqn)
        assert isinstance(class_node, ClassNode)

        self.context.stack_node(class_node)
        self._visit_class_bases(node.bases)
        self.visit(node.decorator_list)
        self.visit(node.body)
        self.context.pop_node()
        
    def _visit_class_bases(self, bases: list[AstExpr]):
        self.context.stack_edge(EdgeType.INHERITS)
        self.visit(bases)
        self.context.pop_edge

    
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
        self.context.stack_node(func_node)
        self._empty_function_local_aliases()
        for arg in node.arguments:
            self.visit(arg)
        with self.context.enter_function():
            self.visit(node.body)
        self._visit_return(node.returns)
        self.context.pop_node()
        
    def _find_fqn(self, alias: str):
        if alias in self.function_local_aliases:
            return self.function_local_aliases[alias]
        if alias in self.local_aliases:
            return self.local_aliases[alias]
        return alias

    def _empty_function_local_aliases(self):
        self.function_local_aliases = {}
        
    def _visit_return(self, returns: AstExpr | None):
        self.context.stack_edge(EdgeType.RETURNS)
        self.visit(returns)
        self.context.pop_edge()
    
    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        target = node.target
        if isinstance(target, AstName) and not self.context.in_function_body:
            fqn = f"{self.current_node.id}::{target.id}"
            variable_node = self.node_registry.get_node(fqn)
            self.context.stack_node(variable_node)
            self.visit(node.annotation)
            self.visit(node.value)
            self.context.pop_node()
        else:
            super().visit_ast_ann_assign(node)

    @override
    def visit_ast_attribute(self, node: AstAttribute):
        self.context.stack_attribute(node.attr)
        self.visit(node.value)
        self.context.empty_attribute()


    @override
    def visit_ast_name(self, node: AstName):
        if node.id in PythonBuiltinType._value2member_map_:
            return
        if not self.current_node or not self.current_edge:
            return
        fqn = self._find_fqn(node.id)
        target_node = self.node_registry.get_node(fqn)
        while self.context.attribute_stack:
            attr = self.context.pop_attribute()
            fqn = f"{target_node.id}::{attr}"
            if self.context.attribute_stack:
                self.current_node.add_edge(EdgeType.READS, fqn)
        self.current_node.add_edge(self.current_edge, fqn)
