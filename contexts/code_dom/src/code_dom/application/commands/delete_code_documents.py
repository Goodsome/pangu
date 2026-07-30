from dataclasses import dataclass
from pathlib import Path
from code_dom.application.ports.repo_provider import RepoProvider
from foundation.building_blocks.command import Command


class DeleteCodeDocumentsCommand(Command):
    paths: list[Path]


@dataclass
class DeleteCodeDocumentsCommandHandler:
    def execute(self, cmd: DeleteCodeDocumentsCommand, uow: RepoProvider) -> None:
        uow.documents.delete_all(cmd.paths)
