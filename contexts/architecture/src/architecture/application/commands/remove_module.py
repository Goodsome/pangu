from dataclasses import dataclass
from architecture.application.ports.module_query_serivce import ModuleQueryService
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.exceptions.module_in_use_exception import ModuleInUseException
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.building_blocks.command import Command


class RemoveModuleCommand(Command):
    fqn: ModuleFqn


@dataclass
class RemoveModuleHandler:
    query_service: ModuleQueryService

    def execute(self, cmd: RemoveModuleCommand, uow: UnitOfWork):
        module = uow.repository.find_by_fqn(cmd.fqn)
        if module is None:
            return
        callers = self.query_service.get_external_dependencies(module.id)
        if callers:
            raise ModuleInUseException(module_fqn=cmd.fqn, callers=callers)
        module.mark_as_deleted()
        uow.repository.delete(module)
        if module.is_package:
            descendant_ids = self.query_service.get_descendant_ids(module.id)
            uow.repository.delete_all(descendant_ids)
