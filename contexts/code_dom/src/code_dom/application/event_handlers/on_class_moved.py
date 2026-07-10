import logging
from dataclasses import dataclass
from code_dom.application.ports.unit_of_work import UnitOfWork
from foundation.integration_events.class_moved import ClassMovedIntegrationEvent

logger = logging.getLogger(__name__)


@dataclass
class OnClassMoved:
    def update_imports(self, event: ClassMovedIntegrationEvent, uow: UnitOfWork):
        for caller_path in event.affected_callers:
            caller = uow.documents.get(caller_path)
            caller.update_imports(event.current_module_fqn, event.target_module_fqn)
            uow.documents.save(caller)
