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
from code_structure.domain.value_objects.parsed_class import ParsedClass


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

    def sync_from_parsed_class(self, parsed_class: ParsedClass) -> None:
        """Sync references, methods and attributes from parsed class"""
        self._sync_references(parsed_class)
        self._sync_methods(parsed_class)
        self._sync_attributes(parsed_class)

    def _sync_references(self, parsed_class: ParsedClass) -> None:
        """Sync class-level references from the class itself, its variables, and functions"""
        self._references.clear()
        for ref in parsed_class.references:
            self.add_reference(ref.target_fqn, alias=ref.alias)
        for parsed_var in parsed_class.variables:
            for ref in parsed_var.references:
                self.add_reference(ref.target_fqn, alias=ref.alias)
        for parsed_func in parsed_class.functions:
            for ref in parsed_func.references:
                self.add_reference(ref.target_fqn, alias=ref.alias)

    def _sync_methods(self, parsed_class: ParsedClass) -> None:
        """Sync methods defined inside the class"""
        new_funcs_by_name = {f.name: f for f in parsed_class.functions}
        
        # Remove methods that no longer exist
        methods_to_remove = [
            m_id for m_id, m in self.methods.items() if m.name not in new_funcs_by_name
        ]
        for m_id in methods_to_remove:
            del self.methods[m_id]

        # Add newly introduced methods
        existing_methods_by_name = {m.name: m for m in self.methods.values()}
        for func_name, parsed_func in new_funcs_by_name.items():
            if func_name not in existing_methods_by_name:
                new_method = MethodSymbol(
                    id=MethodId.create(),
                    name=func_name,
                    fqn=MethodFqn(f"{self.fqn}::{func_name}"),
                )
                self.define_method(new_method)

    def _sync_attributes(self, parsed_class: ParsedClass) -> None:
        """Sync attributes defined inside the class"""
        new_vars_by_name = {v.name: v for v in parsed_class.variables}
        
        # Remove attributes that no longer exist
        attrs_to_remove = [
            a_id for a_id, a in self.attributes.items() if a.name not in new_vars_by_name
        ]
        for a_id in attrs_to_remove:
            del self.attributes[a_id]

        # Add newly introduced attributes
        existing_attrs_by_name = {a.name: a for a in self.attributes.values()}
        for var_name, parsed_var in new_vars_by_name.items():
            if var_name not in existing_attrs_by_name:
                new_attr = AttributeSymbol(
                    id=AttributeId.create(),
                    name=var_name,
                    fqn=AttributeFqn(f"{self.fqn}::{var_name}"),
                )
                self.define_attribute(new_attr)


