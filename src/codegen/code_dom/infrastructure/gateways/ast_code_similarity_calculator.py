from dataclasses import dataclass
from typing import override
from codegen.code_dom.domain.ports.code_formatter import CodeFormatter
from codegen.code_dom.domain.ports.code_similarity_calculator import (
    CodeSimilarityCalculator,
)
import ast
import difflib


@dataclass
class AstCodeSimilarityCalculator(CodeSimilarityCalculator):

    @override
    def calculate_similarity(self, code1: str, code2: str) -> float:
        tree_orig = ast.parse(code1)
        tree_gen = ast.parse(code2)
        tree_orig.body = [
            i for i in tree_orig.body if not isinstance(i, ast.ImportFrom)
        ]
        tree_gen.body = [i for i in tree_gen.body if not isinstance(i, ast.ImportFrom)]
        dump_orig = ast.dump(tree_orig, annotate_fields=True, include_attributes=False)
        dump_gen = ast.dump(tree_gen, annotate_fields=True, include_attributes=False)
        matcher = difflib.SequenceMatcher(
            None,
            dump_orig.replace("(", "\n").splitlines(),
            dump_gen.replace("(", "\n").splitlines(),
        )
        return matcher.ratio()
