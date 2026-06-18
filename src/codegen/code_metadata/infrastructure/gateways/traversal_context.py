from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.edge_type import EdgeType


@dataclass
class Scope:
    node: CodeNode
    aliases: dict[str, CodeNode] = field(default_factory=dict)
    
    def add_alias(self, node: CodeNode, asname: str | None = None):
        name = node.name
        if asname:
            name = asname
        self.aliases[name] = node

@dataclass
class TraversalContext:
    """封装作用域和边类型的状态机"""
    
    scope_stack: list[Scope] = field(default_factory=list)
    is_type_checking: bool = False
    in_function_body: bool = False

    @property
    def current_node(self) -> CodeNode:
        if not self.scope_stack:
            raise ValueError(f"{self.scope_stack} is None")
        return self.scope_stack[-1].node

    @property
    def current_scope(self) -> Scope:
        if not self.scope_stack:
            raise ValueError(f"{self.scope_stack} is None")
        return self.scope_stack[-1]

    @contextmanager
    def visit_node(self, node: CodeNode) -> Generator[None, None, None]:
        """安全地将节点压入栈中，并在退出上下文时弹出"""
        new_scope = Scope(node=node)
        self.scope_stack.append(new_scope)
        try:
            yield
        finally:
            self.scope_stack.pop()

    @contextmanager
    def enter_function(self) -> Generator[None, None, None]:
        """管理是否在函数体内的状态"""
        previous_in_function_body = self.in_function_body
        self.in_function_body = True
        try:
            yield
        finally:
            self.in_function_body = previous_in_function_body

    def add_alias(self, node: CodeNode, asname: str | None = None):
        self.current_scope.add_alias(node, asname=asname)

    def resolve_alias(self, name: str) -> CodeNode | None:
        for scope in reversed(self.scope_stack):
            if name in scope.aliases:
                return scope.aliases[name]
        return None