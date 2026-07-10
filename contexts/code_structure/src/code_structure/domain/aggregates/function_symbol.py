from code_structure.domain.identities.symbol_ids import FunctionId
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import FunctionFqn, SymbolFqn
from code_structure.domain.value_objects.parsed_reference import ParsedReference
from code_structure.domain.value_objects.parsed_function import ParsedFunction
from pydantic import PrivateAttr


class FunctionSymbol(AggregateRoot[FunctionId]):
    name: str
    fqn: FunctionFqn

    _references: list[ParsedReference] = PrivateAttr(default_factory=list)

    @property
    def references(self) -> list[ParsedReference]:
        return list(self._references)

    def add_reference(self, target_fqn: SymbolFqn, alias: str | None = None) -> None:
        self._references.append(ParsedReference(target_fqn=target_fqn, alias=alias))

    def sync_from_parsed_function(self, parsed_function: ParsedFunction) -> None:
        """Sync references from parsed function"""
        self._references.clear()
        for ref in parsed_function.references:
            self.add_reference(ref.target_fqn, alias=ref.alias)
