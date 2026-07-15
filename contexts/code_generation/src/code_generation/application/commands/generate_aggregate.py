from dataclasses import dataclass

from foundation.building_blocks.command import Command
from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString

from code_generation.domain.factories.module_blueprint_factory import (
    ModuleBlueprintFactory,
)
from code_generation.domain.ports.generator import Generator


class GenerateAggregateCommand(Command):
    context: SnakeString
    name: PascalString


@dataclass
class GenerateAggregateCommandHandler:
    generator: Generator

    def execute(self, cmd: GenerateAggregateCommand) -> None:
        factory = ModuleBlueprintFactory()
        aggregate_name = cmd.name
        id_name = f"{aggregate_name}Id"
        identity_blueprint = factory.create_identity(cmd.context, id_name)
        aggregate_blueprint = factory.create_aggregate(
            cmd.context,
            aggregate_name,
            id_blueprint=identity_blueprint,
        )
        repo_port_blueprint = factory.create_repository_port(
            cmd.context, aggregate_name
        )
        self.generator.write_modules(
            modules=[identity_blueprint, aggregate_blueprint, repo_port_blueprint]
        )
