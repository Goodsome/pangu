from dataclasses import dataclass
from code_dom.application.ports.repo_provider import RepoProvider
from foundation.building_blocks.command import Command
from code_dom.domain.aggregates.code_document import CodeDocument


class GenerateCodeCommand(Command):
    code_documents: list[CodeDocument]


@dataclass
class GenerateCodeHandler:
    def execute(self, cmd: GenerateCodeCommand, uow: RepoProvider):
        uow.documents.save_all(cmd.code_documents)
