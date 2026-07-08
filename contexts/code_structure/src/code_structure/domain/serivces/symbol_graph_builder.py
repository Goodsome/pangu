from dataclasses import dataclass

from foundation.common_types.fqns.fqn import (
    AttributeFqn,
    ClassFqn,
    FunctionFqn,
    MethodFqn,
    VariableFqn,
)

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.aggregates.file_module import FileModule
from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.entities.attribute_symbol import AttributeSymbol
from code_structure.domain.entities.method_symbol import MethodSymbol
from code_structure.domain.identities.symbol_ids import (
    AttributeId,
    ClassId,
    FunctionId,
    MethodId,
    VariableId,
    ExternalSymbolId,
)
from code_structure.domain.aggregates.external_symbol import ExternalSymbol
from code_structure.domain.serivces.class_symbol_registry import ClassRegistry
from code_structure.domain.serivces.file_module_registry import FileModuleRegistry
from code_structure.domain.serivces.function_symbol_registry import FunctionRegistry
from code_structure.domain.serivces.variable_symbol_registry import VariableRegistry
from code_structure.domain.serivces.external_symbol_registry import (
    ExternalSymbolRegistry,
)
from code_structure.domain.value_objects.parsed_attribute import ParsedAttribute
from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule
from code_structure.domain.value_objects.parsed_import import ParsedImport
from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_method import ParsedMethod
from code_structure.domain.value_objects.parsed_variable import ParsedVariable


@dataclass
class SymbolGraphBuilder:
    file_module_registry: FileModuleRegistry
    class_registry: ClassRegistry
    function_registry: FunctionRegistry
    variable_registry: VariableRegistry
    external_symbol_registry: ExternalSymbolRegistry

    def build_from_parsed_file_modules(
        self, parsed_file_modules: list[ParsedFileModule]
    ) -> None:
        for parsed_file_module in parsed_file_modules:
            self.build_from_parsed_file_module(parsed_file_module)

    def build_from_parsed_file_module(
        self, parsed_file_module: ParsedFileModule
    ) -> None:
        file_module = self.file_module_registry.get_by_fqn(parsed_file_module.fqn)
        self.file_module_registry.mark_dirty(file_module)
        for parsed_class in parsed_file_module.classes:
            self.build_class_symbol(parsed_class, file_module)
        for parsed_function in parsed_file_module.functions:
            self.build_function_symbol(parsed_function, file_module)
        for parsed_variable in parsed_file_module.variables:
            self.build_variable_symbol(parsed_variable, file_module)
        for parsed_import in parsed_file_module.imports:
            self.build_imports_edge(parsed_import, file_module)

    def build_imports_edge(
        self,
        parsed_import: ParsedImport,
        file_module: FileModule,
    ) -> None:
        is_internal = (
            self.class_registry.contains_fqn(parsed_import.target_fqn)
            or self.function_registry.contains_fqn(parsed_import.target_fqn)
            or self.variable_registry.contains_fqn(parsed_import.target_fqn)
        )
        if not is_internal and not self.external_symbol_registry.contains_fqn(
            parsed_import.target_fqn
        ):
            external_symbol = ExternalSymbol(
                id=ExternalSymbolId.create(),
                name=parsed_import.target_fqn.symbol,
                fqn=parsed_import.target_fqn,
            )
            self.external_symbol_registry.register(external_symbol)
        file_module.imports(parsed_import.target_fqn, alias=parsed_import.alias)

    def build_class_symbol(
        self,
        parsed_class: ParsedClass,
        file_module: FileModule,
    ) -> None:
        class_fqn = ClassFqn(f"{file_module.fqn}::{parsed_class.name}")
        class_symbol = ClassSymbol(
            id=ClassId.create(),
            name=parsed_class.name,
            fqn=class_fqn,
        )
        self.class_registry.register(class_symbol)
        file_module.define_class(class_symbol.id)

        for parsed_attribute in parsed_class.attributes:
            self.build_attribute_symbol(parsed_attribute, class_symbol)
        for parsed_method in parsed_class.methods:
            self.build_method_symbol(parsed_method, class_symbol)

    def build_function_symbol(
        self,
        parsed_function: ParsedFunction,
        file_module: FileModule,
    ) -> None:
        function_fqn = FunctionFqn(f"{file_module.fqn}::{parsed_function.name}")
        function_symbol = FunctionSymbol(
            id=FunctionId.create(),
            name=parsed_function.name,
            fqn=function_fqn,
        )
        self.function_registry.register(function_symbol)
        file_module.define_function(function_symbol.id)

    def build_variable_symbol(
        self,
        parsed_variable: ParsedVariable,
        file_module: FileModule,
    ) -> None:
        variable_fqn = VariableFqn(f"{file_module.fqn}::{parsed_variable.name}")
        variable_symbol = VariableSymbol(
            id=VariableId.create(),
            name=parsed_variable.name,
            fqn=variable_fqn,
        )
        self.variable_registry.register(variable_symbol)
        file_module.define_variable(variable_symbol.id)

    def build_attribute_symbol(
        self,
        parsed_attribute: ParsedAttribute,
        class_symbol: ClassSymbol,
    ) -> None:
        attribute_fqn = AttributeFqn(f"{class_symbol.fqn}::{parsed_attribute.name}")
        attribute_symbol = AttributeSymbol(
            id=AttributeId.create(),
            name=parsed_attribute.name,
            fqn=attribute_fqn,
        )
        class_symbol.define_attribute(attribute_symbol)

    def build_method_symbol(
        self,
        parsed_method: ParsedMethod,
        class_symbol: ClassSymbol,
    ) -> None:
        method_fqn = MethodFqn(f"{class_symbol.fqn}::{parsed_method.name}")
        method_symbol = MethodSymbol(
            id=MethodId.create(),
            name=parsed_method.name,
            fqn=method_fqn,
        )
        class_symbol.define_method(method_symbol)
