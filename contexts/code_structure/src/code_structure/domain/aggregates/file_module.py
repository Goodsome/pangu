from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn
from foundation.common_types.identities.module_id import ModuleId
from pydantic import PrivateAttr

from code_structure.domain.identities.symbol_ids import ClassId, FunctionId, VariableId
from code_structure.domain.value_objects.parsed_import import ParsedImport


class FileModule(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str

    _classes: set[ClassId] = PrivateAttr(default_factory=set)
    _functions: set[FunctionId] = PrivateAttr(default_factory=set)
    _variables: set[VariableId] = PrivateAttr(default_factory=set)
    _imports: list[ParsedImport] = PrivateAttr(default_factory=list)

    @property
    def classes(self) -> frozenset[ClassId]:
        return frozenset(self._classes)

    @property
    def functions(self) -> frozenset[FunctionId]:
        return frozenset(self._functions)

    @property
    def variables(self) -> frozenset[VariableId]:
        return frozenset(self._variables)

    @property
    def imports(self) -> list[ParsedImport]:
        return list(self._imports)

    def define_class(self, class_id: ClassId) -> None:
        self._classes.add(class_id)

    def undefine_class(self, class_id: ClassId) -> None:
        """Remove class definition from module."""
        self._classes.discard(class_id)

    def add_import(
        self,
        target_fqn: SymbolFqn,
        alias: str | None = None,
    ) -> None:
        self._imports.append(ParsedImport(target_fqn=target_fqn, alias=alias))

    def set_imports(self, imports: list[ParsedImport]) -> None:
        self._imports = list(imports)

    def define_function(self, function_id: FunctionId) -> None:
        self._functions.add(function_id)

    def undefine_function(self, function_id: FunctionId) -> None:
        """Remove function definition from module."""
        self._functions.discard(function_id)

    def define_variable(self, variable_id: VariableId) -> None:
        self._variables.add(variable_id)

    def undefine_variable(self, variable_id: VariableId) -> None:
        """Remove variable definition from module."""
        self._variables.discard(variable_id)

    def clear_definitions(self) -> None:
        """Clear all definitions of classes, functions, variables and imports."""
        self._classes.clear()
        self._functions.clear()
        self._variables.clear()
        self._imports.clear()
