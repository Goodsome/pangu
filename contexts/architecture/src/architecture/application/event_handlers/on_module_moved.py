from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.module_moved import ModuleMoved
from architecture.domain.services.fqn_service import FqnService
from foundation.integration_events.module_moved import ModuleMovedIntegrationEvent


@dataclass
class OnModuleMoved:
    def to_integration(self, event: ModuleMoved, uow: UnitOfWork):
        old_path = FqnService.build_path(event.old_fqn, is_package=event.is_package)
        new_path = FqnService.build_path(event.new_fqn, is_package=event.is_package)
        dependencies = uow.repository.get_dependencies(event.module_id)
        ie = ModuleMovedIntegrationEvent(
            old_path=old_path,
            new_path=new_path,
            old_module_fqn=event.old_fqn,
            new_module_fqn=event.new_fqn,
            affected_callers=[
                FqnService.build_path(d, is_package=False) for d in dependencies
            ],
        )
        uow.save_outbox_message(ie)

    def update_fqn_prefix(self, event: ModuleMoved, uow: UnitOfWork):
        uow.repository.update_fqn_prefix(event.old_fqn, event.new_fqn)
