from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId
from pydantic import PrivateAttr

from code_structure.domain.identities.symbol_ids import ClassId, FunctionId, VariableId
from code_structure.domain.mutations.add_defines_edge import AddModuleDefinesEdge, RemoveModuleDefinesEdge


class FileModule(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str

    _classes: set[ClassId] = PrivateAttr(default_factory=set)
    _functions: set[FunctionId] = PrivateAttr(default_factory=set)
    _variables: set[VariableId] = PrivateAttr(default_factory=set)

    def define_class(self, class_id: ClassId) -> None:
        self._classes.add(class_id)
        self.add_mutation(AddModuleDefinesEdge(source_id=self.id, target_id=class_id))

    def undefine_class(self, class_id: ClassId) -> None:
        """Remove class definition from module."""
        self._classes.discard(class_id)
        self.add_mutation(RemoveModuleDefinesEdge(source_id=self.id, target_id=class_id))

    def define_function(self, function_id: FunctionId) -> None:
        self._functions.add(function_id)
        self.add_mutation(AddModuleDefinesEdge(source_id=self.id, target_id=function_id))

    def define_variable(self, variable_id: VariableId) -> None:
        self._variables.add(variable_id)
        self.add_mutation(AddModuleDefinesEdge(source_id=self.id, target_id=variable_id))
