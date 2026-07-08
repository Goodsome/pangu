from code_structure.domain.identities.symbol_ids import FunctionId
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import FunctionFqn, SymbolFqn
from code_structure.domain.mutations.add_defines_edge import AddReferencesEdge


class FunctionSymbol(AggregateRoot[FunctionId]):
    name: str
    fqn: FunctionFqn

    def references(self, target_fqn: SymbolFqn) -> None:
        self.add_mutation(
            AddReferencesEdge(
                source_fqn=self.fqn, target_fqn=target_fqn
            )
        )
