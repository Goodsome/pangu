from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import (
    ClassFqn,
    ModuleFqn,
    MethodFqn,
    AttributeFqn,
)
from pydantic import Field

from code_structure.domain.entities.attribute_symbol import AttributeSymbol
from code_structure.domain.entities.method_symbol import MethodSymbol
from code_structure.domain.identities.symbol_ids import AttributeId, ClassId, MethodId
from code_structure.domain.events.class_moved import ClassMoved
from code_structure.domain.mutations.add_defines_edge import AddClassDefinesEdge


class ClassSymbol(AggregateRoot[ClassId]):
    name: str
    fqn: ClassFqn

    methods: dict[MethodId, MethodSymbol] = Field(default_factory=dict)
    attributes: dict[AttributeId, AttributeSymbol] = Field(default_factory=dict)

    def define_method(self, method: MethodSymbol) -> None:
        self.methods[method.id] = method
        self.add_mutation(AddClassDefinesEdge(source_id=self.id, target_id=method.id))

    def define_attribute(self, attribute: AttributeSymbol) -> None:
        self.attributes[attribute.id] = attribute
        self.add_mutation(
            AddClassDefinesEdge(source_id=self.id, target_id=attribute.id)
        )

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
