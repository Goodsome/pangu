from dataclasses import dataclass

from foundation.building_blocks.command import Command
from pydantic import BaseModel


class CreateDependencyScaffoldCommand(Command): ...


class CreateDependencyScaffoldResult(BaseModel):
    result: str


@dataclass
class CreateDependencyScaffoldCommandHandler:
    
    async def execute(
        self, cmd: CreateDependencyScaffoldCommand
    ) -> CreateDependencyScaffoldResult:
        return CreateDependencyScaffoldResult(result="Dependency scaffolded")
