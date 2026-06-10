from abc import ABC
from abc import abstractmethod
from codegen.code_dom.domain.aggregates.code_document import CodeDocument


class CodeGenerator(ABC):

    @abstractmethod
    def generate(self, code_document: CodeDocument) -> str: ...
