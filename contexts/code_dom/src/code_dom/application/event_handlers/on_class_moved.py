import logging
from dataclasses import dataclass
from code_dom.application.ports.unit_of_work import UnitOfWork
from foundation.integration_events.class_moved import ClassMovedIntegrationEvent

logger = logging.getLogger(__name__)


@dataclass
class OnClassMoved:
    def execute_class_move(self, event: ClassMovedIntegrationEvent, uow: UnitOfWork):
        source_doc = uow.documents.get(event.current_module_path)
        target_doc = uow.documents.get(event.target_module_path)

        class_def = source_doc.remove_class(event.class_name)
        if class_def is None:
            logger.warning(
                "Class %r not found in %s", event.class_name, event.current_module_path
            )
            return

        target_doc.add_class(class_def)

        source_doc.set_imports(event.current_module_deps)
        target_doc.set_imports(event.target_module_deps)

        for caller_path in event.affected_callers:
            caller = uow.documents.get(caller_path)
            caller.move_class_import(
                event.class_name, event.current_module_fqn, event.target_module_fqn
            )
            uow.documents.save(caller)

        uow.documents.save(source_doc)
        uow.documents.save(target_doc)
