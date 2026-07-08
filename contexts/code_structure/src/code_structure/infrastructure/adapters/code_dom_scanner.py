from dataclasses import dataclass
from typing import override

from architecture.domain.services.fqn_service import FqnService
from code_dom.application.queries.get_file_document import (
    GetFileDocumentHandler,
    GetFileDocumentQuery,
)
from code_structure.infrastructure.visitors.module_visitor import ModuleVistior
from foundation.common_types.fqns.fqn import ModuleFqn

from code_structure.domain.ports.symbol_scanner import SymbolScanner
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule


@dataclass
class CodeDomScanner(SymbolScanner):
    get_file_document_handler: GetFileDocumentHandler

    @override
    def scan(self, module_fqns: list[ModuleFqn]) -> list[ParsedFileModule]:
        return [self._scan_file_module(module_fqn) for module_fqn in module_fqns]

    def _scan_file_module(self, module_fqn: ModuleFqn) -> ParsedFileModule:
        file_path = FqnService.build_path(module_fqn, is_package=False)
        result = self.get_file_document_handler.execute(
            GetFileDocumentQuery(file_path=file_path)
        )
        code_document = result.code_document
        visitor = ModuleVistior(module_fqn=module_fqn)
        visitor.visit(code_document.body)
        return ParsedFileModule(
            fqn=module_fqn,
            classes=visitor.classes,
            functions=visitor.functions,
            variables=visitor.variables,
            imports=visitor.imports,
        )

