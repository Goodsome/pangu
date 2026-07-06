from dataclasses import dataclass

from foundation.building_blocks.command import Command
from pydantic import BaseModel, Field
from spike.domain.enums.context_name import ContextName
from spike.domain.enums.scaffold_type import ScaffoldType
from spike.domain.ports.scaffold_builder import ScaffoldBuilder


class CreateDependencyScaffoldCommand(Command):
    scaffold_type: ScaffoldType = Field(description="The type of scaffold")
    context: ContextName = Field(description="The context in which to create the dependency scaffold")
    description: str = Field(description="The description of the dependency")


class CreateDependencyScaffoldResult(BaseModel):
    result: str


@dataclass
class CreateDependencyScaffoldCommandHandler:

    scaffold_builder: ScaffoldBuilder
    
    async def execute(
        self, cmd: CreateDependencyScaffoldCommand
    ) -> CreateDependencyScaffoldResult:
        result = await self.scaffold_builder.build(
            scaffold_type=cmd.scaffold_type,
            context=cmd.context,
            description=cmd.description,
        )
        return CreateDependencyScaffoldResult(result=result)
