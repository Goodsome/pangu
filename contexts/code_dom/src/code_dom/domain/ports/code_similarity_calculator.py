from abc import ABC
from abc import abstractmethod


class CodeSimilarityCalculator(ABC):
    @abstractmethod
    def calculate_similarity(self, code1: str, code2: str) -> float: ...
