from dataclasses import dataclass

from architecture.application.ports.module_query_serivce import ModuleQueryService
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.module_moved import ModuleMoved
from architecture.domain.services.fqn_service import FqnService

from codegen.shared.application.integration_events.module_moved import (
    ModuleMovedIntegrationEvent,
)


@dataclass
class OnModuleMoved:
    query_service: ModuleQueryService

    def to_integration(self, event: ModuleMoved, uow: UnitOfWork):
        old_path = str(FqnService.build_path(event.old_fqn))
        new_path = str(FqnService.build_path(event.new_fqn))
        dependencies = self.query_service.get_external_dependencies(event.module_id)
        ie = ModuleMovedIntegrationEvent(
            old_path=old_path,
            new_path=new_path,
            old_module_fqn=event.old_fqn,
            new_module_fqn=event.new_fqn,
            affected_callers=[str(FqnService.build_path(d)) for d in dependencies],
        )
        uow.save_outbox_message(ie)
        yield from []

    def update_fqn_prefix(self, event: ModuleMoved, uow: UnitOfWork):
        uow.repository.update_fqn_prefix(event.old_fqn, event.new_fqn)
        yield from []
