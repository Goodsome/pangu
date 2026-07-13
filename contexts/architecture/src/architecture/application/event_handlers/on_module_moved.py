from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.events.file_module_moved import FileModuleMoved
from architecture.domain.events.package_module_moved import PackageModuleMoved
from architecture.domain.services.fqn_service import FqnService
from foundation.integration_events.module_moved import ModuleMovedIntegrationEvent


@dataclass
class OnModuleMoved:
    def to_integration_from_file(self, event: FileModuleMoved, uow: UnitOfWork):
        old_path = FqnService.build_path(event.old_fqn, is_package=False)
        new_path = FqnService.build_path(event.new_fqn, is_package=False)
        dependencies = uow.file_modules.get_dependencies(event.module_id)
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

    def to_integration_from_package(self, event: PackageModuleMoved, uow: UnitOfWork):
        old_path = FqnService.build_path(event.old_fqn, is_package=True)
        new_path = FqnService.build_path(event.new_fqn, is_package=True)
        ie = ModuleMovedIntegrationEvent(
            old_path=old_path,
            new_path=new_path,
            old_module_fqn=event.old_fqn,
            new_module_fqn=event.new_fqn,
            affected_callers=[],
        )
        uow.save_outbox_message(ie)

    def update_fqn_prefix_from_file(self, event: FileModuleMoved, uow: UnitOfWork):
        uow.file_modules.update_fqn_prefix(event.old_fqn, event.new_fqn)

    def update_fqn_prefix_from_package(
        self, event: PackageModuleMoved, uow: UnitOfWork
    ):
        uow.packages.update_fqn_prefix(event.old_fqn, event.new_fqn)
