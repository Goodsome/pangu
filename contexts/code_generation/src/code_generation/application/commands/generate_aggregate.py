from dataclasses import dataclass

from code_dom.interfaces.api import CodeDomApi
from code_structure.interfaces.api import CodeStructureApi
from foundation.building_blocks.command import Command
from foundation.common_types.pascal_string import PascalString

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.module_blueprint_factory import (
    ModuleBlueprintFactory,
)


class GenerateAggregateCommand(Command):
    context: str
    name: str


@dataclass
class GenerateAggregateCommandHandler:
    factory: ModuleBlueprintFactory
    code_dom_api: CodeDomApi
    code_structure_api: CodeStructureApi

    def execute(self, cmd: GenerateAggregateCommand) -> None:
        agg_modules = self.factory.create_aggregate_modules(cmd.context, cmd.name)

        existing_aggs = self.code_structure_api.get_aggregates(cmd.context)
        all_agg_names = {agg.name for agg in existing_aggs}
        all_agg_names.add(str(PascalString(cmd.name)))

        uow_module = self.factory.create_unit_of_work(
            cmd.context, list(all_agg_names)
        )

        all_modules = [*agg_modules, uow_module]
        name_module_map = self._build_name_module_map(all_modules)

        docs = [m.to_code_document(name_module_map) for m in all_modules]
        self.code_dom_api.save_documents(docs)

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
