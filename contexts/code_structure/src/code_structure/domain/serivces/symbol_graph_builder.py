from dataclasses import dataclass

from code_structure.domain.serivces.file_module_registry import FileModuleRegistry
from foundation.common_types.fqns.fqn import ClassFqn, FunctionFqn, VariableFqn

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.identities.symbol_ids import ClassId, FunctionId, VariableId
from code_structure.domain.serivces.class_symbol_registry import ClassRegistry
from code_structure.domain.serivces.function_symbol_registry import FunctionRegistry
from code_structure.domain.serivces.variable_symbol_registry import VariableRegistry
from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule
from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_variable import ParsedVariable


@dataclass
class SymbolGraphBuilder:
    file_module_registry: FileModuleRegistry
    class_registry: ClassRegistry
    function_registry: FunctionRegistry
    variable_registry: VariableRegistry

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
        for parsed_function in parsed_file_module.functions:
            self.build_function_symbol(parsed_function, parsed_file_module)
        for parsed_variable in parsed_file_module.variables:
            self.build_variable_symbol(parsed_variable, parsed_file_module)

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

    def build_function_symbol(
        self,
        parsed_function: ParsedFunction,
        parsed_file_module: ParsedFileModule,
    ) -> None:
        function_fqn = FunctionFqn(f"{parsed_file_module.fqn}::{parsed_function.name}")
        function_symbol = FunctionSymbol(
            id=FunctionId.create(),
            name=parsed_function.name,
            fqn=function_fqn,
        )
        self.function_registry.register(function_symbol)
        file_module = self.file_module_registry.get_by_fqn(parsed_file_module.fqn)
        file_module.define_function(function_symbol.id)
        self.file_module_registry.mark_dirty(file_module)

    def build_variable_symbol(
        self,
        parsed_variable: ParsedVariable,
        parsed_file_module: ParsedFileModule,
    ) -> None:
        variable_fqn = VariableFqn(f"{parsed_file_module.fqn}::{parsed_variable.name}")
        variable_symbol = VariableSymbol(
            id=VariableId.create(),
            name=parsed_variable.name,
            fqn=variable_fqn,
        )
        self.variable_registry.register(variable_symbol)
        file_module = self.file_module_registry.get_by_fqn(parsed_file_module.fqn)
        file_module.define_variable(variable_symbol.id)
        self.file_module_registry.mark_dirty(file_module)
