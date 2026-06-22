from dataclasses import dataclass

from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.module_created import ModuleCreated
from architecture.domain.services.fqn_service import FqnService
from architecture.domain.value_objects.fqn import ModuleFqn

from codegen.shared.application.integration_events.module_created import (
    ModuleCreatedIntegrationEvent,
)


@dataclass
class OnModuleCreated:

    def to_integration(self, event: ModuleCreated, uow: UnitOfWork):
        module_fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(module_fqn, is_package=event.is_package)
        if event.is_package:
            module_path /= "__init__.py"

        ie = ModuleCreatedIntegrationEvent(
            module_fqn=event.module_fqn,
            module_path=module_path,
            is_package=event.is_package,
        )
        uow.save_outbox_message(ie)
        yield from []
