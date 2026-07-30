from dataclasses import dataclass

from code_dom.interfaces.api import CodeDomApi
from code_structure.interfaces.api import CodeStructureApi
from foundation.building_blocks.command import Command
from foundation.common_types.pascal_string import PascalString

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.module_blueprint_factory import (
    ModuleBlueprintFactory,
)


class DeleteAggregateCommand(Command):
    context: str
    name: str


@dataclass
class DeleteAggregateCommandHandler:
    factory: ModuleBlueprintFactory
    code_dom_api: CodeDomApi
    code_structure_api: CodeStructureApi

    def execute(self, cmd: DeleteAggregateCommand) -> None:
        agg_modules = self.factory.create_aggregate_modules(cmd.context, cmd.name)
        paths_to_delete = [m.to_physical_path() for m in agg_modules]
        self.code_dom_api.delete_documents(paths_to_delete)

        existing_aggs = self.code_structure_api.get_aggregates(cmd.context)
        target_name = str(PascalString(cmd.name))
        remaining_agg_names = [
            agg.name for agg in existing_aggs if agg.name != target_name
        ]

        if remaining_agg_names:
            uow_module = self.factory.create_unit_of_work(
                cmd.context, remaining_agg_names
            )
            name_module_map = self._build_name_module_map([uow_module])
            self.code_dom_api.save_documents(
                [uow_module.to_code_document(name_module_map)]
            )
        else:
            uow_module = self.factory.create_unit_of_work(cmd.context, [])
            self.code_dom_api.delete_documents([uow_module.to_physical_path()])

    def _build_name_module_map(self, modules: list[ModuleBlueprint]) -> dict[str, str]:
        name_module_map: dict[str, str] = {}
        external_symbols: set[str] = set()

        for m in modules:
            local_symbols = m.collect_local_symbols()
            for s_name in local_symbols:
                name_module_map[s_name] = str(m.path)
            external_symbols.update(m.needed_symbols - local_symbols)

        if external_symbols:
            symbols = self.code_structure_api.get_symbols(list(external_symbols))
            for sym in symbols:
                name_module_map[sym.name] = str(sym.module_fqn)

        return name_module_map
