from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn
from foundation.common_types.identities.module_id import ModuleId

from code_structure.domain.identities.symbol_ids import ClassId, FunctionId, VariableId
from code_structure.domain.value_objects.parsed_import import ParsedImport


class FileModule(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str

    classes: set[ClassId]
    functions: set[FunctionId]
    variables: set[VariableId]
    imports: list[ParsedImport]

    def define_class(self, class_id: ClassId) -> None:
        self.classes.add(class_id)

    def undefine_class(self, class_id: ClassId) -> None:
        """Remove class definition from module."""
        self.classes.discard(class_id)

    def add_import(
        self,
        target_fqn: SymbolFqn,
        alias: str | None = None,
    ) -> None:
        self.imports.append(ParsedImport(target_fqn=target_fqn, alias=alias))

    def set_imports(self, imports: list[ParsedImport]) -> None:
        self.imports = list(imports)

    def define_function(self, function_id: FunctionId) -> None:
        self.functions.add(function_id)

    def undefine_function(self, function_id: FunctionId) -> None:
        """Remove function definition from module."""
        self.functions.discard(function_id)

    def define_variable(self, variable_id: VariableId) -> None:
        self.variables.add(variable_id)

    def undefine_variable(self, variable_id: VariableId) -> None:
        """Remove variable definition from module."""
        self.variables.discard(variable_id)
