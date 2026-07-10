from code_structure.domain.identities.symbol_ids import VariableId
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import VariableFqn, SymbolFqn
from code_structure.domain.value_objects.parsed_reference import ParsedReference
from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from pydantic import PrivateAttr


class VariableSymbol(AggregateRoot[VariableId]):
    name: str
    fqn: VariableFqn

    _references: list[ParsedReference] = PrivateAttr(default_factory=list)

    @property
    def references(self) -> list[ParsedReference]:
        return list(self._references)

    def add_reference(self, target_fqn: SymbolFqn, alias: str | None = None) -> None:
        self._references.append(ParsedReference(target_fqn=target_fqn, alias=alias))

    def sync_from_parsed_variable(self, parsed_variable: ParsedVariable) -> None:
        """Sync references from parsed variable"""
        self._references.clear()
        for ref in parsed_variable.references:
            self.add_reference(ref.target_fqn, alias=ref.alias)
