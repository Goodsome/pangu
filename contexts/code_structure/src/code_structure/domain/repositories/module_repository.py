from abc import ABC
from code_structure.domain.aggregates.module import Module
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.repository import Repository


class ModuleRepository(Repository[Module, ModuleId], ABC):
    ...
    