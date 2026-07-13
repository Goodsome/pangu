from dataclasses import dataclass

from foundation.building_blocks.command import Command
from pydantic import BaseModel, Field
from spike.domain.ports.scaffold_builder import ScaffoldBuilder
from spike.domain.value_objects.scaffold_payload import ScaffoldPayload


class CreateDependencyScaffoldCommand(Command):
    scaffold_payload: ScaffoldPayload = Field(
        description="The payload for the scaffold"
    )


class CreateDependencyScaffoldResult(BaseModel):
    result: str


@dataclass
class CreateDependencyScaffoldCommandHandler:
    scaffold_builder: ScaffoldBuilder

    async def execute(
        self, cmd: CreateDependencyScaffoldCommand
    ) -> CreateDependencyScaffoldResult:
        result = await self.scaffold_builder.build(
            scaffold_payload=cmd.scaffold_payload,
        )
        return CreateDependencyScaffoldResult(result=result)
