from dataclasses import dataclass
from pathlib import Path
from architecture.infrastructure.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command


class InitProjectGraphCommand(Command):
    root_path: Path


@dataclass
class InitProjectGraphHandler:

    def execute(self, cmd: InitProjectGraphCommand, uow: UnitOfWork):
        print(cmd)