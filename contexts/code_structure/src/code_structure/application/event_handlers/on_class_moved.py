from dataclasses import dataclass

from architecture.domain.services.fqn_service import FqnService
from code_structure.application.ports.unit_of_work import UnitOfWork
from code_structure.domain.events.class_moved import ClassMoved
from foundation.integration_events.class_moved import ClassMovedIntegrationEvent


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
            FqnService.build_path(m, is_package=False)
            for m in affected_modules
        ]

        ie = ClassMovedIntegrationEvent(
            class_name=class_name,
            current_module_path=current_module_path,
            target_module_path=target_module_path,
            current_module_fqn=str(event.old_fqn),
            target_module_fqn=str(event.new_fqn),
            affected_callers=affected_callers,
        )
        uow.save_outbox_message(ie)
