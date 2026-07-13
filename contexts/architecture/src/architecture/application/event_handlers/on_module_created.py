from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.file_module_created import FileModuleCreated
from architecture.domain.events.package_module_created import PackageModuleCreated
from architecture.domain.services.fqn_service import FqnService
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.integration_events.module_created import ModuleCreatedIntegrationEvent


@dataclass
class OnModuleCreated:
    def to_integration_from_file(self, event: FileModuleCreated, uow: UnitOfWork):
        module_fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(module_fqn, is_package=False)
        ie = ModuleCreatedIntegrationEvent(
            module_fqn=event.module_fqn,
            module_path=module_path,
            is_package=False,
        )
        uow.save_outbox_message(ie)

    def to_integration_from_package(self, event: PackageModuleCreated, uow: UnitOfWork):
        module_fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(module_fqn, is_package=True)
        module_path /= "__init__.py"
        ie = ModuleCreatedIntegrationEvent(
            module_fqn=event.module_fqn,
            module_path=module_path,
            is_package=True,
        )
        uow.save_outbox_message(ie)
