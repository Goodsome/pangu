from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import (
    ClassFqn,
    ModuleFqn,
    MethodFqn,
    AttributeFqn,
    SymbolFqn,
)
from pydantic import Field, PrivateAttr

from code_structure.domain.entities.attribute_symbol import AttributeSymbol
from code_structure.domain.entities.method_symbol import MethodSymbol
from code_structure.domain.identities.symbol_ids import AttributeId, ClassId, MethodId
from code_structure.domain.events.class_moved import ClassMoved
from code_structure.domain.value_objects.parsed_reference import ParsedReference


class ClassSymbol(AggregateRoot[ClassId]):
    name: str
    fqn: ClassFqn

    methods: dict[MethodId, MethodSymbol] = Field(default_factory=dict)
    attributes: dict[AttributeId, AttributeSymbol] = Field(default_factory=dict)
    _references: list[ParsedReference] = PrivateAttr(default_factory=list)

    @property
    def references(self) -> list[ParsedReference]:
        return list(self._references)

    def define_method(self, method: MethodSymbol) -> None:
        self.methods[method.id] = method

    def define_attribute(self, attribute: AttributeSymbol) -> None:
        self.attributes[attribute.id] = attribute

    def move(self, target_module_fqn: ModuleFqn) -> None:
        """Move class and its inner methods/attributes to target module"""
        old_fqn = self.fqn
        self.fqn = ClassFqn(f"{target_module_fqn}::{self.name}")
        for method in self.methods.values():
            method.fqn = MethodFqn(f"{self.fqn}::{method.name}")
        for attribute in self.attributes.values():
            attribute.fqn = AttributeFqn(f"{self.fqn}::{attribute.name}")
        self.add_domain_event(
            ClassMoved(
                class_id=self.id,
                old_fqn=old_fqn,
                new_fqn=self.fqn,
            )
        )

    def add_reference(self, target_fqn: SymbolFqn, alias: str | None = None) -> None:
        self._references.append(ParsedReference(target_fqn=target_fqn, alias=alias))
