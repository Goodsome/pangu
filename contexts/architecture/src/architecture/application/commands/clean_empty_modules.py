from dataclasses import dataclass

from architecture.application.ports.module_query_serivce import ModuleQueryService
from architecture.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.command import Command


class CleanEmptyModulesCommand(Command):
    pass


@dataclass
class CleanEmptyModulesHandler:
    query_service: ModuleQueryService

    def execute(self, cmd: CleanEmptyModulesCommand, uow: UnitOfWork):
        empty_fqns = self.query_service.find_empty_leaf_packages()
        for fqn in empty_fqns:
            module = uow.repository.find_by_fqn(fqn)
            if module is None:
                continue
            module.mark_as_deleted()
            uow.repository.delete(module)
