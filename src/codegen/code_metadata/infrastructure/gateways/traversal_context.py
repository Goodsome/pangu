from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator

from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.enums.edge_type import EdgeType

@dataclass
class TraversalContext:
    """封装作用域和边类型的状态机"""
    node_stack: list[CodeNode] = field(default_factory=list)
    edge_stack: list[EdgeType] = field(default_factory=list)
    attribute_stack: list[str] = field(default_factory=list)
    
    is_type_checking: bool = False
    in_function_body: bool = False

    @property
    def current_node(self) -> CodeNode:
        if not self.node_stack:
            raise ValueError(f"{self.node_stack} is None")
        return self.node_stack[-1]

    @property
    def current_edge(self) -> EdgeType | None:
        if not self.edge_stack:
            return None
        return self.edge_stack[-1]

    @contextmanager
    def visit_node(self, node: CodeNode) -> Generator[None, None, None]:
        """安全地将节点压入栈中，并在退出上下文时弹出"""
        self.node_stack.append(node)
        try:
            yield
        finally:
            self.node_stack.pop()

    @contextmanager
    def visit_edge(self, edge: EdgeType) -> Generator[None, None, None]:
        """安全地将边类型压入栈中，并在退出上下文时弹出"""
        self.edge_stack.append(edge)
        try:
            yield
        finally:
            self.edge_stack.pop()

    @contextmanager
    def visit_attribute(self, attribute: str) -> Generator[None, None, None]:
        """安全地将属性压入栈中，并在退出上下文时弹出"""
        self.attribute_stack.append(attribute)
        try:
            yield
        finally:
            self.attribute_stack.pop()

    @contextmanager
    def enter_function(self) -> Generator[None, None, None]:
        """管理是否在函数体内的状态"""
        previous_in_function_body = self.in_function_body
        self.in_function_body = True
        try:
            yield
        finally:
            self.in_function_body = previous_in_function_body

    def stack_node(self, node: CodeNode):
        self.node_stack.append(node)

    def pop_node(self) -> CodeNode:
        return self.node_stack.pop()
        
    def stack_edge(self, edge: EdgeType):
        self.edge_stack.append(edge)

    def pop_edge(self):
        self.edge_stack.pop()

    def stack_attribute(self, attribute: str):
        self.attribute_stack.append(attribute)
    
    def pop_attribute(self):
        return self.attribute_stack.pop()
    
    def empty_attribute(self):
        self.attribute_stack.clear()
    