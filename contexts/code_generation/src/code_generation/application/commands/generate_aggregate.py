from dataclasses import dataclass

from code_structure.interfaces.api import CodeStructureApi
from foundation.building_blocks.command import Command
from foundation.common_types.pascal_string import PascalString

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
    factory: ModuleBlueprintFactory
    code_structure_api: CodeStructureApi

    def execute(self, cmd: GenerateAggregateCommand) -> None:
        agg_modules = self.factory.create_aggregate_modules(cmd.context, cmd.name)

        existing_aggs = self.code_structure_api.get_aggregates(cmd.context)
        all_agg_names = {agg.name for agg in existing_aggs}
        all_agg_names.add(str(PascalString(cmd.name)))

        uow_module = self.factory.create_unit_of_work(
            cmd.context, list(all_agg_names)
        )

        self.generator.write_modules(modules=[*agg_modules, uow_module])
