from dataclasses import dataclass

from code_structure.interfaces.api import CodeStructureApi
from foundation.building_blocks.command import Command
from foundation.common_types.pascal_string import PascalString

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
    code_structure_api: CodeStructureApi

    def execute(self, cmd: DeleteAggregateCommand) -> None:
        agg_modules = self.factory.create_aggregate_modules(cmd.context, cmd.name)
        self.generator.remove_modules(modules=agg_modules)

        existing_aggs = self.code_structure_api.get_aggregates(cmd.context)
        target_name = str(PascalString(cmd.name))
        remaining_agg_names = [
            agg.name for agg in existing_aggs if agg.name != target_name
        ]

        if remaining_agg_names:
            uow_module = self.factory.create_unit_of_work(
                cmd.context, remaining_agg_names
            )
            self.generator.write_modules(modules=[uow_module])
        else:
            uow_module = self.factory.create_unit_of_work(cmd.context, [])
            self.generator.remove_modules(modules=[uow_module])