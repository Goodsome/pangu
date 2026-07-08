from code_structure.domain.identities.symbol_ids import VariableId
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import VariableFqn, SymbolFqn
from code_structure.domain.mutations.add_defines_edge import AddReferencesEdge


class VariableSymbol(AggregateRoot[VariableId]):
    name: str
    fqn: VariableFqn

    def references(self, target_fqn: SymbolFqn, alias: str | None = None) -> None:
        self.add_mutation(
            AddReferencesEdge(
                source_fqn=self.fqn, target_fqn=target_fqn, alias=alias
            )
        )
