from dataclasses import dataclass

from code_structure.domain.serivces.file_module_registry import FileModuleRegistry
from foundation.common_types.fqns.fqn import ClassFqn

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import ClassId
from code_structure.domain.serivces.class_symbol_registry import ClassRegistry
from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule


@dataclass
class SymbolGraphBuilder:
    file_module_registry: FileModuleRegistry
    class_registry: ClassRegistry

    def build_from_parsed_file_modules(
        self, parsed_file_modules: list[ParsedFileModule]
    ) -> None:
        for parsed_file_module in parsed_file_modules:
            self.build_from_parsed_file_module(parsed_file_module)

    def build_from_parsed_file_module(
        self, parsed_file_module: ParsedFileModule
    ) -> None:
        for parsed_class in parsed_file_module.classes:
            self.build_class_symbol(parsed_class, parsed_file_module)

    def build_class_symbol(
        self,
        parsed_class: ParsedClass,
        parsed_file_module: ParsedFileModule,
    ) -> None:
        class_fqn = ClassFqn(f"{parsed_file_module.fqn}::{parsed_class.name}")
        class_symbol = ClassSymbol(
            id=ClassId.create(),
            name=parsed_class.name,
            fqn=class_fqn,
        )
        self.class_registry.register(class_symbol)
        file_module = self.file_module_registry.get_by_fqn(parsed_file_module.fqn)
        file_module.define_class(class_symbol.id)
        self.file_module_registry.mark_dirty(file_module)
        
