from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.file_module_deleted import FileModuleDeleted
from architecture.domain.events.package_module_deleted import PackageModuleDeleted
from architecture.domain.services.fqn_service import FqnService
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.integration_events.module_deleted import ModuleDeletedIntegrationEvent


@dataclass
class OnModuleDeleted:
    def to_integration_from_file(
        self, event: FileModuleDeleted, uow: UnitOfWork
    ):
        fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(fqn, is_package=False)
        ie = ModuleDeletedIntegrationEvent(
            module_fqn=str(event.module_fqn),
            module_path=module_path,
            is_package=False,
        )
        uow.save_outbox_message(ie)

    def to_integration_from_package(
        self, event: PackageModuleDeleted, uow: UnitOfWork
    ):
        fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(fqn, is_package=True)
        ie = ModuleDeletedIntegrationEvent(
            module_fqn=str(event.module_fqn),
            module_path=module_path,
            is_package=True,
        )
        uow.save_outbox_message(ie)
