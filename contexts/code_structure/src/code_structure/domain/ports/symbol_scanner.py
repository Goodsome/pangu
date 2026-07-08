from abc import ABC, abstractmethod

from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule
from foundation.common_types.fqns.fqn import ModuleFqn


class SymbolScanner(ABC):
    @abstractmethod
    def scan(self, module_fqns: list[ModuleFqn]) -> list[ParsedFileModule]: ...
