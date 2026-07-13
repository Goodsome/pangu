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


class AstToMatchPattern:
    @staticmethod
    def to_match_pattern(node: ast.pattern) -> MatchPattern:
        match node:
            case ast.MatchValue():
                return AstToMatchPattern.from_match_value(node)
            case ast.MatchSingleton():
                return AstToMatchPattern.from_match_singleton(node)
            case ast.MatchSequence():
                return AstToMatchPattern.from_match_sequence(node)
            case ast.MatchMapping():
                return AstToMatchPattern.from_match_mapping(node)
            case ast.MatchClass():
                return AstToMatchPattern.from_match_class(node)
            case ast.MatchStar():
                return AstToMatchPattern.from_match_star(node)
            case ast.MatchAs():
                return AstToMatchPattern.from_match_as(node)
            case ast.MatchOr():
                return AstToMatchPattern.from_match_or(node)
            case _:
                raise NotImplementedError(f"Unsupported ast.pattern type: {type(node)}")

    @staticmethod
    def from_match_value(node: ast.MatchValue) -> MatchValue:
        return MatchValue(value=ast.unparse(node.value) if node.value else None)

    @staticmethod
    def from_match_singleton(node: ast.MatchSingleton) -> MatchSingleton:
        return MatchSingleton(value=node.value)

    @staticmethod
    def from_match_sequence(node: ast.MatchSequence) -> MatchSequence:
        return MatchSequence(
            patterns=[AstToMatchPattern.to_match_pattern(p) for p in node.patterns]
        )

    @staticmethod
    def from_match_mapping(node: ast.MatchMapping) -> MatchMapping:
        return MatchMapping(
            keys=[ast.unparse(k) for k in node.keys],
            patterns=[AstToMatchPattern.to_match_pattern(p) for p in node.patterns],
            rest=node.rest,
        )

    @staticmethod
    def from_match_class(node: ast.MatchClass) -> MatchClass:
        return MatchClass(
            cls=ast.unparse(node.cls),
            patterns=[AstToMatchPattern.to_match_pattern(p) for p in node.patterns],
            kwd_attrs=list(node.kwd_attrs),
            kwd_patterns=[
                AstToMatchPattern.to_match_pattern(p) for p in node.kwd_patterns
            ],
        )

    @staticmethod
    def from_match_star(node: ast.MatchStar) -> MatchStar:
        return MatchStar(name=node.name)

    @staticmethod
    def from_match_as(node: ast.MatchAs) -> MatchAs:
        return MatchAs(
            pattern=(
                AstToMatchPattern.to_match_pattern(node.pattern)
                if node.pattern
                else None
            ),
            name=node.name,
        )

    @staticmethod
    def from_match_or(node: ast.MatchOr) -> MatchOr:
        return MatchOr(
            patterns=[AstToMatchPattern.to_match_pattern(p) for p in node.patterns]
        )
