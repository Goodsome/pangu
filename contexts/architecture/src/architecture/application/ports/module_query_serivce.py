from abc import ABC, abstractmethod

from architecture.domain.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn


class ModuleQueryService(ABC):

    @abstractmethod
    def get_external_dependencies(self, id: ModuleId) -> list[ModuleFqn]: ...
    
    @abstractmethod
    def get_child_ids(self, id: ModuleId) -> list[ModuleId]: ...
    
    @abstractmethod
    def get_descendant_ids(self, id: ModuleId) -> list[ModuleId]: ...

    @abstractmethod
    def find_empty_leaf_packages(self) -> list[ModuleFqn]: ...