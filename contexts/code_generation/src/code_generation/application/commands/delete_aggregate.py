from dataclasses import dataclass

from foundation.building_blocks.command import Command

from code_generation.domain.factories.module_blueprint_factory import (
    ModuleBlueprintFactory,
)
from code_generation.domain.ports.generator import Generator


class DeleteAggregateCommand(Command):
    context: str
    name: str


@dataclass
class DeleteAggregateCommandHandler:
    generator: Generator
    factory: ModuleBlueprintFactory

    def execute(self, cmd: DeleteAggregateCommand) -> None:
        modules = self.factory.create_aggregate_modules(cmd.context, cmd.name)
        self.generator.remove_modules(modules)