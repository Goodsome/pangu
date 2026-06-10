from __future__ import annotations
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.component import UnionComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_kind import ComponentKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.code_metadata.infrastructure.orm_models.component_v2_model import (
    ClassComponentV2Model,
)
from codegen.code_metadata.infrastructure.orm_models.component_v2_model import (
    ComponentV2Model,
)
from codegen.code_metadata.infrastructure.orm_models.component_v2_model import (
    UnionComponentV2Model,
)


class ComponentV2Mapper:

    @classmethod
    def to_domain(cls, orm_model: ComponentV2Model) -> Component:
        match orm_model.kind:
            case ComponentKind.CLASS:
                return cls._to_class_component(orm_model)
            case ComponentKind.UNION:
                return cls._to_union_component(orm_model)
            case _:
                raise ValueError(f"Unknown component kind: {orm_model.kind}")

    @classmethod
    def _to_class_component(cls, orm_model: ComponentV2Model) -> ClassComponent:
        assert isinstance(orm_model, ClassComponentV2Model)
        return ClassComponent(
            id=ComponentId.reconstitute(orm_model.id),
            module_id=ModuleId.reconstitute(orm_model.module_id),
            type=ComponentType(orm_model.type),
            name=orm_model.name,
            description=orm_model.description,
            context=orm_model.context,
            layer=ArchitectureLayer(orm_model.layer),
            bases=[TypeDef.model_validate(t) for t in orm_model.bases],
            attributes=[Attribute.model_validate(a) for a in orm_model.attributes],
            behaviors=[Behavior.model_validate(b) for b in orm_model.behaviors],
        )

    @classmethod
    def _to_union_component(cls, orm_model: ComponentV2Model) -> UnionComponent:
        assert isinstance(orm_model, UnionComponentV2Model)
        return UnionComponent(
            id=ComponentId.reconstitute(orm_model.id),
            module_id=ModuleId.reconstitute(orm_model.module_id),
            type=ComponentType(orm_model.type),
            name=orm_model.name,
            context=orm_model.context,
            layer=ArchitectureLayer(orm_model.layer),
            members=[ReferenceTarget.model_validate(m) for m in orm_model.members],
            discriminator=orm_model.discriminator,
            description="",
        )

    @classmethod
    def to_orm(cls, domain_entity: Component) -> ComponentV2Model:
        match domain_entity.kind:
            case ComponentKind.CLASS:
                return cls._class_to_orm(domain_entity)
            case ComponentKind.UNION:
                return cls._union_to_orm(domain_entity)
            case _:
                raise ValueError(f"Unknown component kind: {domain_entity.kind}")

    @classmethod
    def _class_to_orm(cls, domain_entity: ClassComponent) -> ClassComponentV2Model:
        return ClassComponentV2Model(
            id=domain_entity.id.value,
            module_id=domain_entity.module_id.value,
            kind=domain_entity.kind.value,
            type=domain_entity.type.value,
            name=domain_entity.name,
            description=domain_entity.description,
            context=domain_entity.context,
            layer=domain_entity.layer.value,
            bases=[t.model_dump(mode="json") for t in domain_entity.bases],
            attributes=[a.model_dump(mode="json") for a in domain_entity.attributes],
            behaviors=[b.model_dump(mode="json") for b in domain_entity.behaviors],
        )

    @classmethod
    def _union_to_orm(cls, domain_entity: UnionComponent) -> UnionComponentV2Model:
        return UnionComponentV2Model(
            id=domain_entity.id.value,
            module_id=domain_entity.module_id.value,
            kind=domain_entity.kind.value,
            type=domain_entity.type.value,
            name=domain_entity.name,
            description="",
            context=domain_entity.context,
            layer=domain_entity.layer.value,
            members=[m.model_dump(mode="json") for m in domain_entity.members],
            discriminator=domain_entity.discriminator,
        )
