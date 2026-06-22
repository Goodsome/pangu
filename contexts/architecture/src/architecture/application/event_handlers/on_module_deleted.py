from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.module_deleted import ModuleDeleted
from architecture.domain.services.fqn_service import FqnService
from architecture.domain.value_objects.fqn import ModuleFqn
from foundation.integration_events.module_deleted import ModuleDeletedIntegrationEvent


@dataclass
class OnModuleDeleted:
    def to_integration(self, event: ModuleDeleted, uow: UnitOfWork):
        fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(fqn, is_package=event.is_package)
        ie = ModuleDeletedIntegrationEvent(
            module_fqn=str(event.module_fqn),
            module_path=module_path,
            is_package=event.is_package,
        )
        uow.save_outbox_message(ie)
        yield from []
