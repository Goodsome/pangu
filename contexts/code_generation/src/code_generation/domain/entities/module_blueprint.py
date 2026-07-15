from foundation.building_blocks.entity import Entity
from foundation.common_types.fqns.fqn import ModuleFqn

from code_generation.domain.value_objects.import_def import ImportDef
from code_generation.domain.value_objects.symbol_def import SymbolDef


class ModuleBlueprint(Entity):
    path: ModuleFqn
    imports: list[ImportDef]
    symbols: list[SymbolDef]

    def collect_import_symbols(self) -> set[str]:
        return {s.name for s in self.imports}
