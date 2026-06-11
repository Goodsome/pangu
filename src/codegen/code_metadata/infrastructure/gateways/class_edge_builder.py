from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import ExternalNode
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_bin_op import AstBinOp
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_list import AstList
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_tuple import AstTuple
from codegen.code_metadata.domain.value_objects.ast_subscript import AstSubscript
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class ClassEdgeBuilder:
    class_node: ClassNode
    class_def: AstClassDef
    node_registry: NodeRegistry
    local_aliases: dict[str, str]
    function_local_aliases: dict[str, str] = field(default_factory=dict)
    scope_stack: list[CodeNode] = field(default_factory=list)
    edge_stack: list[EdgeType] = field(default_factory=list)
    attribute_stack: list[str] = field(default_factory=list)

    def _find_fqn(self, alias: str):
        if alias in self.function_local_aliases:
            return self.function_local_aliases[alias]
        if alias in self.local_aliases:
            return self.local_aliases[alias]
        return alias

    def _empty_function_local_aliases(self):
        self.function_local_aliases = {}

    @property
    def current_node(self) -> CodeNode | None:
        if not self.scope_stack:
            return None
        return self.scope_stack[-1]

    @property
    def current_edge(self) -> EdgeType | None:
        if not self.edge_stack:
            return None
        return self.edge_stack[-1]

    def build(self):
        self._visit_stmt(self.class_def)

    def _visit_stmt(self, stmt: AstStmt):
        match stmt:
            case AstClassDef():
                self._visit_class_def(stmt)
            case AstFunctionDef():
                self._visit_function_def(stmt)
            case AstAnnAssign():
                self._visit_ann_assign(stmt)
            case AstAssign():
                self._visit_assign(stmt)
            case AstExprStmt():
                pass
            case AstPass():
                pass
            case _:
                raise ValueError(
                    f"Unsupported: stmt={stmt!r}\n self.current_node={self.current_node!r}"
                )

    def _visit_class_def(self, class_def: AstClassDef):
        self.scope_stack.append(self.class_node)
        self._visit_class_bases(class_def.bases)
        for body in class_def.body:
            self._visit_stmt(body)
        self.scope_stack.pop()

    def _visit_class_bases(self, bases: list[AstExpr]):
        self.edge_stack.append(EdgeType.INHERITS)
        for base in bases:
            self._visit_expr(base)
        self.edge_stack.pop()

    def _visit_function_def(self, func_def: AstFunctionDef):
        func_fqn = f"{self.class_node.id}::{func_def.name}"
        if func_def.is_overload:
            func_fqn = f"{func_fqn}::<overload_{func_def.lineno}>"
        elif func_def.is_setter_property:
            func_fqn = f"{func_fqn}::<setter>"
        elif func_def.is_deleter_property:
            func_fqn = f"{func_fqn}::<deleter>"
        elif func_def.is_expression_property:
            func_fqn = f"{func_fqn}::<expression>"
        func_node = self.node_registry.get_node(func_fqn)
        assert isinstance(func_node, MethodNode), func_node
        self.scope_stack.append(func_node)
        self._empty_function_local_aliases()
        self._visit_return(func_def.returns)
        
        # for body in func_def.body:
            # self._visit_stmt(body)
            
        self.scope_stack.pop()

    def _visit_assign(self, assign: AstAssign):
        match self.current_node:
            case ClassNode():
                self._visit_assign_in_class(assign)
            case _:
                raise ValueError(f"Unsupported node type: {self.current_node}")

    def _visit_assign_in_class(self, assign: AstAssign):
        if not assign.targets:
            return
        if not len(assign.targets) == 1:
            return
        target = assign.targets[0]
        if not isinstance(target, AstName):
            return
        fqn = f"{self.class_node.id}::{target.id}"
        node = self.node_registry.get_node(fqn)
        self.scope_stack.append(node)
        self.scope_stack.pop()

    def _visit_ann_assign(self, ann_assign: AstAnnAssign):
        match self.current_node:
            case ClassNode():
                self._visit_ann_assign_in_class(ann_assign)
            case _:
                raise ValueError(f"Unsupported node type: {self.current_node}")

    def _visit_ann_assign_in_class(self, ann_assign: AstAnnAssign):
        target = ann_assign.target
        if not isinstance(target, AstName):
            return
        fqn = f"{self.class_node.id}::{target.id}"
        node = self.node_registry.get_node(fqn)
        self.scope_stack.append(node)
        self._visit_ann_assign_annotation(ann_assign.annotation)
        self.scope_stack.pop()

    def _visit_ann_assign_annotation(self, annotation: AstExpr | None):
        self.edge_stack.append(EdgeType.TYPED_AS)
        self._visit_expr(annotation)
        self.edge_stack.pop()

    def _visit_return(self, returns: AstExpr | None):
        self.edge_stack.append(EdgeType.RETURNS)
        self._visit_expr(returns)
        self.edge_stack.pop()

    def _visit_expr(self, expr: AstExpr | None):
        if expr is None:
            return
        match expr:
            case AstConstant():
                pass
            case AstName():
                self._visit_name(expr)
            case AstBinOp(left=left, right=right):
                self._visit_expr(left)
                self._visit_expr(right)
            case AstSubscript(value=value, slice=slice):
                self._visit_expr(value)
                self._visit_expr(slice)
            case AstTuple(elts=elts) | AstList(elts=elts):
                for elt in elts:
                    self._visit_expr(elt)
            case AstAttribute():
                self._visit_attribute(expr)
            case _:
                raise ValueError(f"Unsupported expr type: {expr}\n")

    def _visit_name(self, name: AstName):
        if name.id in PythonBuiltinType._value2member_map_:
            return
        if not self.current_node or not self.current_edge:
            return
        fqn = self._find_fqn(name.id)
        target_node = self.node_registry.get_node(fqn)
        while self.attribute_stack:
            attr = self.attribute_stack.pop()
            fqn = f"{target_node.id}::{attr}"
            if self.attribute_stack:
                self.current_node.add_edge(EdgeType.READS, fqn)
        self.current_node.add_edge(self.current_edge, fqn)

    def _visit_attribute(self, attr: AstAttribute):
        self.attribute_stack.append(attr.attr)
        self._visit_expr(attr.value)
        self.attribute_stack = []
