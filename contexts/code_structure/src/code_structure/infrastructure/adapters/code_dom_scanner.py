from dataclasses import dataclass
from typing import override

from architecture.domain.services.fqn_service import FqnService
from code_dom.application.queries.get_file_document import (
    GetFileDocumentHandler,
    GetFileDocumentQuery,
)
from code_structure.infrastructure.visitors.module_visitor import ModuleVistior
from code_structure.infrastructure.visitors.module_pre_scan_visitor import (
    ModulePreScanVisitor,
)
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn

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
        if not result.file_exists:
            return ParsedFileModule(
                fqn=module_fqn,
                classes=[],
                functions=[],
                variables=[],
                imports=[],
                exists=False,
            )
        code_document = result.code_document

        # 1. 预扫描以提取 imports 和本地顶级声明符号名字
        pre_visitor = ModulePreScanVisitor(module_fqn=module_fqn)
        pre_visitor.visit(code_document.body)

        scope_symbols: dict[str, SymbolFqn] = {}
        for imp in pre_visitor.imports:
            name_key = imp.alias or imp.target_fqn.symbol
            scope_symbols[name_key] = imp.target_fqn
        for name in pre_visitor.local_symbol_names:
            scope_symbols[name] = SymbolFqn(f"{module_fqn}::{name}")

        # 2. 带 references 解析的正式扫描
        visitor = ModuleVistior(
            module_fqn=module_fqn,
            scope_symbols=scope_symbols,
        )
        visitor.visit(code_document.body)

        return ParsedFileModule(
            fqn=module_fqn,
            classes=visitor.classes,
            functions=visitor.functions,
            variables=visitor.variables,
            imports=pre_visitor.imports,
            exists=True,
        )
