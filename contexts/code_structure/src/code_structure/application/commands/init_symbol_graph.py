from dataclasses import dataclass
from code_structure.application.ports.unit_of_work import UnitOfWork
from code_structure.domain.ports.symbol_scanner import SymbolScanner
from code_structure.domain.serivces.class_symbol_registry import ClassRegistry
from code_structure.domain.serivces.file_module_registry import FileModuleRegistry
from code_structure.domain.serivces.function_symbol_registry import FunctionRegistry
from code_structure.domain.serivces.symbol_graph_builder import SymbolGraphBuilder
from code_structure.domain.serivces.variable_symbol_registry import VariableRegistry
from foundation.building_blocks.command import Command


class InitSymbolGraphCommand(Command):
    ...


@dataclass
class InitSymbolGraphCommandHandler:
    symbol_scanner: SymbolScanner

    def execute(self, cmd: InitSymbolGraphCommand, uow: UnitOfWork) -> None:
        uow.graph_admin.purge_data()
        file_modules = uow.file_modules.get_all_modules()
        module_fqns = [module.fqn for module in file_modules]
        parsed_file_modules = self.symbol_scanner.scan(module_fqns)
        class_registry = ClassRegistry()
        function_registry = FunctionRegistry()
        variable_registry = VariableRegistry()
        file_module_registry = FileModuleRegistry.init(file_modules)
        symbol_graph_builder = SymbolGraphBuilder(
            file_module_registry=file_module_registry,
            class_registry=class_registry,
            function_registry=function_registry,
            variable_registry=variable_registry,
        )
        symbol_graph_builder.build_from_parsed_file_modules(parsed_file_modules)
        dirty_file_modules = list(file_module_registry.dirty_file_modules)
        dirty_class_symbols = list(class_registry.dirty_classes)
        dirty_function_symbols = list(function_registry.dirty_functions)
        dirty_variable_symbols = list(variable_registry.dirty_variables)
        uow.file_modules.save_all(dirty_file_modules)
        uow.classes.add_all(dirty_class_symbols)
        uow.functions.add_all(dirty_function_symbols)
        uow.variables.add_all(dirty_variable_symbols)
