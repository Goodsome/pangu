from dataclasses import dataclass

from architecture.domain.services.fqn_service import FqnService
from code_structure.application.ports.unit_of_work import UnitOfWork
from code_structure.domain.events.class_moved import ClassMoved
from foundation.integration_events.class_moved import (
    ClassMovedIntegrationEvent,
    ModuleDepDict,
)


@dataclass
class OnClassMoved:
    def to_integration(self, event: ClassMoved, uow: UnitOfWork) -> None:
        class_name = event.new_fqn.symbol
        current_module_path = FqnService.build_path(
            event.old_fqn.module_fqn, is_package=False
        )
        target_module_path = FqnService.build_path(
            event.new_fqn.module_fqn, is_package=False
        )

        affected_modules = uow.classes.find_affected_callers(event.class_id)
        affected_callers = [
            FqnService.build_path(m, is_package=False) for m in affected_modules
        ]

        current_module_deps: list[ModuleDepDict] = [
            {
                "module": str(dep.target_fqn.module_fqn),
                "symbol": dep.target_fqn.symbol,
                "alias": dep.alias,
            }
            for dep in uow.file_modules.get_external_dependencies(
                event.old_fqn.module_fqn
            )
        ]
        target_module_deps: list[ModuleDepDict] = [
            {
                "module": str(dep.target_fqn.module_fqn),
                "symbol": dep.target_fqn.symbol,
                "alias": dep.alias,
            }
            for dep in uow.file_modules.get_external_dependencies(
                event.new_fqn.module_fqn
            )
        ]

        ie = ClassMovedIntegrationEvent(
            class_name=class_name,
            current_module_path=current_module_path,
            target_module_path=target_module_path,
            current_module_fqn=str(event.old_fqn.module_fqn),
            target_module_fqn=str(event.new_fqn.module_fqn),
            affected_callers=affected_callers,
            current_module_deps=current_module_deps,
            target_module_deps=target_module_deps,
        )
        uow.save_outbox_message(ie)

    def update_module_imports(self, event: ClassMoved, uow: UnitOfWork) -> None:
        source_module = uow.file_modules.get_by_fqn(event.old_fqn.module_fqn)
        target_module = uow.file_modules.get_by_fqn(event.new_fqn.module_fqn)

        source_deps = uow.file_modules.get_external_dependencies(source_module.fqn)
        target_deps = uow.file_modules.get_external_dependencies(target_module.fqn)

        source_module.set_imports(source_deps)
        target_module.set_imports(target_deps)

        uow.file_modules.save(source_module)
        uow.file_modules.save(target_module)
