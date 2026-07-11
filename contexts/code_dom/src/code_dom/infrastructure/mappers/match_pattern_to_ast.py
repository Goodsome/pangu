import ast
from code_dom.domain.value_objects.match_pattern import MatchAs
from code_dom.domain.value_objects.match_pattern import MatchClass
from code_dom.domain.value_objects.match_pattern import MatchMapping
from code_dom.domain.value_objects.match_pattern import MatchOr
from code_dom.domain.value_objects.match_pattern import MatchPattern
from code_dom.domain.value_objects.match_pattern import MatchSequence
from code_dom.domain.value_objects.match_pattern import MatchSingleton
from code_dom.domain.value_objects.match_pattern import MatchStar
from code_dom.domain.value_objects.match_pattern import MatchValue


class MatchPatternToAst:

    @staticmethod
    def to_node(pattern: MatchPattern) -> ast.pattern:
        match pattern:
            case MatchValue():
                return MatchPatternToAst.from_match_value(pattern)
            case MatchSingleton():
                return MatchPatternToAst.from_match_singleton(pattern)
            case MatchSequence():
                return MatchPatternToAst.from_match_sequence(pattern)
            case MatchMapping():
                return MatchPatternToAst.from_match_mapping(pattern)
            case MatchClass():
                return MatchPatternToAst.from_match_class(pattern)
            case MatchStar():
                return MatchPatternToAst.from_match_star(pattern)
            case MatchAs():
                return MatchPatternToAst.from_match_as(pattern)
            case MatchOr():
                return MatchPatternToAst.from_match_or(pattern)
            case _:
                raise NotImplementedError(
                    f"Unsupported MatchPattern type: {type(pattern)}, pattern={pattern!r}"
                )

    @staticmethod
    def from_match_value(pattern: MatchValue) -> ast.MatchValue:
        return ast.MatchValue(
            value=ast.parse(pattern.value, mode="eval").body if pattern.value else None
        )

    @staticmethod
    def from_match_singleton(pattern: MatchSingleton) -> ast.MatchSingleton:
        return ast.MatchSingleton(value=pattern.value)

    @staticmethod
    def from_match_sequence(pattern: MatchSequence) -> ast.MatchSequence:
        return ast.MatchSequence(
            patterns=[MatchPatternToAst.to_node(p) for p in pattern.patterns]
        )

    @staticmethod
    def from_match_mapping(pattern: MatchMapping) -> ast.MatchMapping:
        return ast.MatchMapping(
            keys=[ast.parse(k, mode="eval").body for k in pattern.keys],
            patterns=[MatchPatternToAst.to_node(p) for p in pattern.patterns],
            rest=pattern.rest,
        )

    @staticmethod
    def from_match_class(pattern: MatchClass) -> ast.MatchClass:
        return ast.MatchClass(
            cls=ast.parse(pattern.cls, mode="eval").body,
            patterns=[MatchPatternToAst.to_node(p) for p in pattern.patterns],
            kwd_attrs=pattern.kwd_attrs,
            kwd_patterns=[MatchPatternToAst.to_node(p) for p in pattern.kwd_patterns],
        )

    @staticmethod
    def from_match_star(pattern: MatchStar) -> ast.MatchStar:
        return ast.MatchStar(name=pattern.name)

    @staticmethod
    def from_match_as(pattern: MatchAs) -> ast.MatchAs:
        return ast.MatchAs(
            pattern=(
                MatchPatternToAst.to_node(pattern.pattern) if pattern.pattern else None
            ),
            name=pattern.name,
        )

    @staticmethod
    def from_match_or(pattern: MatchOr) -> ast.MatchOr:
        return ast.MatchOr(
            patterns=[MatchPatternToAst.to_node(p) for p in pattern.patterns]
        )
