import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import override
from foundation.system.file_system_port import FileSystemPort
from architecture.application.ports.code_scanner import CodeScanner
from architecture.domain.value_objects.parsed_module import ParsedModule


@dataclass
class ImportVisitor(ast.NodeVisitor):
    raw_imports: set[str] = field(default_factory=set)

    @override
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.raw_imports.add(alias.name)
        self.generic_visit(node)

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.raw_imports.add(node.module)
        self.generic_visit(node)


class ModuleDependencyExtractor:
    def extract_imports_from_source(self, source_code: str) -> list[str]:
        try:
            tree = ast.parse(source_code)
            visitor = ImportVisitor()
            visitor.visit(tree)
            return list(visitor.raw_imports)
        except SyntaxError:
            return []


@dataclass
class FileSystemCodeScanner(CodeScanner):
    file_system: FileSystemPort

    @override
    def scan_directory(self, root_path: Path) -> list[ParsedModule]:
        files = self.file_system.list_directory_recursively(
            path=root_path, pattern="*.py"
        )
        results: list[ParsedModule] = []
        for file in files:
            results.append(self.parse_file(file))
        return results

    @override
    def scan_files(self, paths: list[Path]) -> list[ParsedModule]:
        results: list[ParsedModule] = []
        for path in paths:
            results.append(self.parse_file(path))
        return results

    @override
    def parse_file(self, path: Path) -> ParsedModule:
        code = self.file_system.read_file(path)
        extractor = ModuleDependencyExtractor()
        raw_imports = extractor.extract_imports_from_source(code)
        return ParsedModule(file_path=path, raw_imports=raw_imports)
