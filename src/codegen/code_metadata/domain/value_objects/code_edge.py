from typing import Annotated
from typing import Literal
from pydantic import Field
from pydantic import TypeAdapter
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.shared.domain.core.value_object import ValueObject


class _BaseEdge(ValueObject):
    fqn: Fqn
    direction: EdgeDirection

    @property
    def node_name(self) -> str:
        if "::" in self.fqn:
            name = self.fqn.rsplit("::")[-1]
        elif "." in self.fqn:
            name = self.fqn.rsplit(".")[-1]
        else:
            name = self.fqn
        return name


class ImportsEdge(_BaseEdge):
    kind: Literal[EdgeType.IMPORTS] = EdgeType.IMPORTS
    asname: str | None = None
    is_type_checking: bool = False


class ContainsEdge(_BaseEdge):
    kind: Literal[EdgeType.CONTAINS] = EdgeType.CONTAINS


class DefinesEdge(_BaseEdge):
    kind: Literal[EdgeType.DEFINES] = EdgeType.DEFINES


class DefinesModuleEdge(_BaseEdge):
    kind: Literal[EdgeType.DEFINES_MODULE] = EdgeType.DEFINES_MODULE


class ExportsEdge(_BaseEdge):
    kind: Literal[EdgeType.EXPORTS] = EdgeType.EXPORTS


class InheritsEdge(_BaseEdge):
    kind: Literal[EdgeType.INHERITS] = EdgeType.INHERITS


class ImplementsEdge(_BaseEdge):
    kind: Literal[EdgeType.IMPLEMENTS] = EdgeType.IMPLEMENTS


class CallsEdge(_BaseEdge):
    kind: Literal[EdgeType.CALLS] = EdgeType.CALLS


class ReadsEdge(_BaseEdge):
    kind: Literal[EdgeType.READS] = EdgeType.READS


class WritesEdge(_BaseEdge):
    kind: Literal[EdgeType.WRITES] = EdgeType.WRITES


class TypedAsEdge(_BaseEdge):
    kind: Literal[EdgeType.TYPED_AS] = EdgeType.TYPED_AS


class ReturnsEdge(_BaseEdge):
    kind: Literal[EdgeType.RETURNS] = EdgeType.RETURNS


class AcceptsEdge(_BaseEdge):
    kind: Literal[EdgeType.ACCEPTS] = EdgeType.ACCEPTS


class OverridesEdge(_BaseEdge):
    kind: Literal[EdgeType.OVERRIDDES] = EdgeType.OVERRIDDES


CodeEdge = Annotated[
    ImportsEdge
    | ContainsEdge
    | DefinesEdge
    | DefinesModuleEdge
    | ExportsEdge
    | InheritsEdge
    | ImplementsEdge
    | CallsEdge
    | ReadsEdge
    | WritesEdge
    | TypedAsEdge
    | ReturnsEdge
    | AcceptsEdge
    | OverridesEdge,
    Field(discriminator="kind"),
]
_edge_adapter: TypeAdapter[CodeEdge] = TypeAdapter(CodeEdge)


def create_edge(kind: EdgeType, fqn: str, direction: EdgeDirection) -> CodeEdge:
    """从 EdgeType 动态构造对应的 Edge 值对象。"""
    return _edge_adapter.validate_python(
        {"kind": kind, "fqn": fqn, "direction": direction}
    )
