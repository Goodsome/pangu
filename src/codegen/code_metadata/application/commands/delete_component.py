from dataclasses import dataclass
from codegen.code_metadata.application.dtos.delete_component_command import (
    DeleteComponentCommand,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork


@dataclass
class DeleteComponent:
    uow: UnitOfWork[ComponentRepository]

    def execute(self, cmd: DeleteComponentCommand) -> None:
        c_id = ComponentId.reconstitute(cmd.component_id)
        with self.uow:
            component = self.uow.repository.get(c_id)
            self.uow.repository.delete(component)
            self.uow.commit()
