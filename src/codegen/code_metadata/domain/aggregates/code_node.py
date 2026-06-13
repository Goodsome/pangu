from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.domain_events.node_deleted import NodeDeleted
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeParam
from codegen.code_metadata.domain.value_objects.code_edge import (
    CodeEdge,
    ContainsEdge,
    DefinesEdge,
    ImportsEdge,
    InheritsEdge,
    create_edge,
)
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class _BaseNode(AggregateRoot[Fqn]):
    name: str
    description: str | None = Field(default=None)
    outbound_edges: list[CodeEdge] = Field(default_factory=list)

    def _add_edge(self, edge: CodeEdge):
        if edge in self.outbound_edges:
            return
        self.outbound_edges.append(edge)

    def _add_edge_by_type(self, type: EdgeType, fqn: str) -> CodeEdge:
        edge = create_edge(kind=type, fqn=fqn, direction=EdgeDirection.OUT)
        self._add_edge(edge)
        return edge

    def add_edge(self, type: EdgeType, fqn: str):
        self._add_edge_by_type(type, fqn)

    def parent_fqn(self) -> str:
        splits = re.split("[.|::]", self.id)
        return ".".join(splits[:-1])

    def mark_deleted(self) -> None:
        event = NodeDeleted(
            node_id=self.id,
            node_kind=self.kind,
        )
        self.add_domain_event(event)


class DirectoryNode(_BaseNode):
    """目录节点：kind 固定为 DIRECTORY。"""

    kind: Literal[CodeNodeKind.DIRECTORY] = CodeNodeKind.DIRECTORY


class FileNode(_BaseNode):
    """文件节点：kind 固定为 FILE。"""

    kind: Literal[CodeNodeKind.FILE] = CodeNodeKind.FILE


class ModuleNode(_BaseNode):
    """模块节点：kind 固定为 MODULE，由文件节点自动派生。"""

    kind: Literal[CodeNodeKind.MODULE] = CodeNodeKind.MODULE
    is_package: bool = False
    exprs: list[AstExpr] = Field(default_factory=list)

    @property
    def is_empty(self):
        return not any(
            edge
            for edge in self.outbound_edges
            if isinstance(edge, (ContainsEdge, DefinesEdge))
        )

    def contains(self, node: ModuleNode):
        edge = ContainsEdge(fqn=node.id, direction=EdgeDirection.OUT)
        self._add_edge(edge)

    def defines(self, node: ClassNode | FunctionNode | VariableNode):
        edge = DefinesEdge(fqn=node.id, direction=EdgeDirection.OUT)
        self._add_edge(edge)

    def imports(
        self,
        node: ExternalNode | ClassNode | FunctionNode | VariableNode,
        asname: str | None = None,
        is_type_checking: bool = False,
    ):
        edge = ImportsEdge(
            fqn=node.id,
            direction=EdgeDirection.OUT,
            asname=asname,
            is_type_checking=is_type_checking,
        )
        self._add_edge(edge)

    def get_parent_by_level(self, level: int) -> str:
        if level == 0:
            return self.id
        parts = self.id.split(".")
        if level >= len(parts):
            raise ValueError(
                f"Level {level} is greater than the depth of the module {self.id}"
            )
        return ".".join(parts[:-level])

    def get_physical_path(self) -> Path:
        path = Path("src") / self.id.replace(".", "/")
        if not self.is_package:
            path = path.with_suffix(".py")
        return path


class ClassNode(_BaseNode):
    """类节点：kind 固定为 CLASS，由模块节点的 AST 类定义派生。"""

    kind: Literal[CodeNodeKind.CLASS] = CodeNodeKind.CLASS
    decorator_list: list[AstExpr] = Field(default_factory=list)
    bases: list[AstExpr] = Field(default_factory=list)
    type_params: list[AstTypeParam] = Field(default_factory=list)

    def defines(self, node: MethodNode | VariableNode):
        edge = DefinesEdge(fqn=node.id, direction=EdgeDirection.OUT)
        self._add_edge(edge)

    def inherits(self, node: ClassNode | ExternalNode, base: AstExpr):
        edge = InheritsEdge(fqn=node.id, direction=EdgeDirection.OUT)
        self._add_edge(edge)


class FunctionNode(_BaseNode):
    """函数节点：kind 固定为 FUNCTION，由模块节点的 AST 函数定义派生。"""

    kind: Literal[CodeNodeKind.FUNCTION] = CodeNodeKind.FUNCTION
    is_async: bool = False
    decorator_list: list[AstExpr] = Field(default_factory=list)
    returns: AstExpr | None = None
    body: list[AstStmt] = Field(default_factory=list)

    def defines(self, node: VariableNode):
        edge = DefinesEdge(fqn=node.id, direction=EdgeDirection.OUT)
        self._add_edge(edge)

    def add_returns(self, node: ClassNode | ExternalNode | VariableNode):
        self._add_edge_by_type(EdgeType.RETURNS, node.id)


class MethodNode(_BaseNode):
    """方法节点：kind 固定为 METHOD，由类节点的 AST 函数定义派生。"""

    kind: Literal[CodeNodeKind.METHOD] = CodeNodeKind.METHOD
    is_async: bool = False
    decorator_list: list[AstExpr] = Field(default_factory=list)
    returns: AstExpr | None = None
    body: list[AstStmt] = Field(default_factory=list)

    def defines(self, node: VariableNode):
        edge = DefinesEdge(fqn=node.id, direction=EdgeDirection.OUT)
        self._add_edge(edge)

    def add_returns(self, node: ClassNode | ExternalNode | VariableNode):
        self._add_edge_by_type(EdgeType.RETURNS, node.id)


class VariableNode(_BaseNode):
    """变量节点：kind 固定为 VARIABLE，由模块节点的 AST 赋值语句派生。"""

    kind: Literal[CodeNodeKind.VARIABLE] = CodeNodeKind.VARIABLE
    annotation: AstExpr | None = None
    value: AstExpr | None = None


class ExternalNode(_BaseNode):
    """外部节点：kind 固定为 EXTERNAL，表示项目外部的依赖（第三方库、标准库等）。"""

    kind: Literal[CodeNodeKind.EXTERNAL] = CodeNodeKind.EXTERNAL


CodeNode = Annotated[
    DirectoryNode
    | FileNode
    | ModuleNode
    | ClassNode
    | FunctionNode
    | MethodNode
    | VariableNode
    | ExternalNode,
    Field(discriminator="kind"),
]
