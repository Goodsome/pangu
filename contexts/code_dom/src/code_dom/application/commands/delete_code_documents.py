from dataclasses import dataclass
from pathlib import Path
from code_dom.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.command import Command


class DeleteCodeDocumentsCommand(Command):
    paths: list[Path]
    

@dataclass
class DeleteCodeDocumentsCommandHandler:

    def execute(self, cmd: DeleteCodeDocumentsCommand, uow: UnitOfWork) -> None:
        uow.documents.delete_all(cmd.paths)
        