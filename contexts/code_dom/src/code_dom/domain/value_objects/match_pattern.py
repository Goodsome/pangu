from __future__ import annotations
from typing import Annotated
from typing import Literal
from typing import Optional
from pydantic import Field
from pydantic import TypeAdapter
from code_dom.domain.enums.ast_match_pattern_kind import (
    AstMatchPatternKind,
)
from foundation.building_blocks.value_object import ValueObject


class MatchValue(ValueObject):
    """Matches a constant or identifier value."""

    kind: Literal[AstMatchPatternKind.MATCH_VALUE] = AstMatchPatternKind.MATCH_VALUE
    value: Optional[str] = None


class MatchSingleton(ValueObject):
    """Matches True, False, or None."""

    kind: Literal[AstMatchPatternKind.MATCH_SINGLETON] = (
        AstMatchPatternKind.MATCH_SINGLETON
    )
    value: Optional[bool] = None


class MatchSequence(ValueObject):
    """Matches a sequence pattern [p1, p2, ...]."""

    kind: Literal[AstMatchPatternKind.MATCH_SEQUENCE] = (
        AstMatchPatternKind.MATCH_SEQUENCE
    )
    patterns: list[MatchPattern] = Field(default_factory=list)


class MatchMapping(ValueObject):
    """Matches a mapping pattern {k1: p1, ...}."""

    kind: Literal[AstMatchPatternKind.MATCH_MAPPING] = AstMatchPatternKind.MATCH_MAPPING
    keys: list[str] = Field(default_factory=list)
    patterns: list[MatchPattern] = Field(default_factory=list)
    rest: Optional[str] = None


class MatchClass(ValueObject):
    """Matches a class pattern Cls(p1, p2, ...)."""

    kind: Literal[AstMatchPatternKind.MATCH_CLASS] = AstMatchPatternKind.MATCH_CLASS
    cls: str = ""
    patterns: list[MatchPattern] = Field(default_factory=list)
    kwd_attrs: list[str] = Field(default_factory=list)
    kwd_patterns: list[MatchPattern] = Field(default_factory=list)


class MatchStar(ValueObject):
    """Matches *name or *_ in a sequence pattern."""

    kind: Literal[AstMatchPatternKind.MATCH_STAR] = AstMatchPatternKind.MATCH_STAR
    name: Optional[str] = None


class MatchAs(ValueObject):
    """Matches pattern as name, or a capture pattern."""

    kind: Literal[AstMatchPatternKind.MATCH_AS] = AstMatchPatternKind.MATCH_AS
    pattern: Optional[MatchPattern] = None
    name: Optional[str] = None


class MatchOr(ValueObject):
    """Matches p1 | p2 | ... ."""

    kind: Literal[AstMatchPatternKind.MATCH_OR] = AstMatchPatternKind.MATCH_OR
    patterns: list[MatchPattern] = Field(default_factory=list)


MatchPattern = Annotated[
    MatchValue
    | MatchSingleton
    | MatchSequence
    | MatchMapping
    | MatchClass
    | MatchStar
    | MatchAs
    | MatchOr,
    Field(discriminator="kind"),
]
match_pattern_adapter: TypeAdapter[MatchPattern] = TypeAdapter(MatchPattern)
MatchSequence.model_rebuild()
MatchMapping.model_rebuild()
MatchClass.model_rebuild()
MatchAs.model_rebuild()
MatchOr.model_rebuild()
