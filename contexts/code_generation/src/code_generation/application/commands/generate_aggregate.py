from dataclasses import dataclass

from foundation.building_blocks.command import Command

from code_generation.domain.factories.module_blueprint_factory import (
    ModuleBlueprintFactory,
)
from code_generation.domain.ports.generator import Generator


class GenerateAggregateCommand(Command):
    context: str
    name: str


@dataclass
class GenerateAggregateCommandHandler:
    generator: Generator

    def execute(self, cmd: GenerateAggregateCommand) -> None:
        factory = ModuleBlueprintFactory()
        id_name = f"{cmd.name}Id"
        identity_blueprint = factory.create_identity(cmd.context, id_name)
        aggregate_blueprint = factory.create_aggregate(
            cmd.context,
            cmd.name,
            id_blueprint=identity_blueprint,
        )
        self.generator.write_modules(modules=[identity_blueprint, aggregate_blueprint])
