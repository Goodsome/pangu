from abc import ABC, abstractmethod
from architecture.domain.aggregates.module import Module
from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.ports.repository import Repository



class ModuleRepository(Repository[Module, ModuleId], ABC):
    ...