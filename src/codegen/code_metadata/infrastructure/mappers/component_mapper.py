from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.component import UnionComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_kind import ComponentKind
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.ast_stmt import ast_stmt_adapter
from codegen.code_metadata.domain.value_objects.expr_def import expr_def_adapter
from codegen.code_metadata.domain.value_objects.scenario import Scenario
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.code_metadata.infrastructure.orm_models.attribute_model import (
    AttributeModel,
)
from codegen.code_metadata.infrastructure.orm_models.behavior_model import BehaviorModel
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    ClassComponentModel,
)
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    ComponentModel,
)
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    UnionComponentModel,
)


class ComponentMapper:
    """负责 Component 聚合根及其所有子实体、值对象在 Domain Model 和 ORM Model 之间的互相转换。"""

    @classmethod
    def to_dto(cls, orm_model: ComponentModel) -> ComponentDto:
        return ComponentDto(
            id=str(orm_model.id),
            kind=orm_model.kind,
            type=orm_model.type,
            name=orm_model.name,
            description=orm_model.description,
            context=orm_model.context,
            layer=orm_model.layer,
        )

    @classmethod
    def to_domain(cls, orm_model: ComponentModel) -> ClassComponent | UnionComponent:
        match orm_model.kind:
            case ComponentKind.CLASS:
                return cls._to_class_component(orm_model)
            case ComponentKind.UNION:
                return cls._to_union_component(orm_model)
            case _:
                raise ValueError(f"Unknown component kind: {orm_model.kind}")

    @classmethod
    def _to_class_component(cls, orm_model: ComponentModel) -> ClassComponent:
        assert isinstance(orm_model, ClassComponentModel)
        return ClassComponent(
            id=ComponentId.reconstitute(orm_model.id),
            type=ComponentType(orm_model.type),
            name=orm_model.name,
            description=orm_model.description,
            context=orm_model.context,
            layer=ArchitectureLayer(orm_model.layer),
            bases=[TypeDef.model_validate(t) for t in orm_model.bases],
            attributes=[cls._attr_to_domain(attr) for attr in orm_model.attributes],
            behaviors=[cls._behavior_to_domain(beh) for beh in orm_model.behaviors],
        )

    @classmethod
    def _to_union_component(cls, orm_model: ComponentModel) -> UnionComponent:
        assert isinstance(orm_model, UnionComponentModel)
        return UnionComponent(
            id=ComponentId.reconstitute(orm_model.id),
            type=ComponentType(orm_model.type),
            name=orm_model.name,
            context=orm_model.context,
            layer=ArchitectureLayer(orm_model.layer),
            discriminator=orm_model.discriminator,
            description="",
        )

    @classmethod
    def _behavior_to_domain(cls, orm_model: BehaviorModel) -> Behavior:
        return Behavior(
            id=BehaviorId.reconstitute(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            scenarios=[Scenario.model_validate(s) for s in orm_model.scenarios],
            inputs=[cls._attr_to_domain(attr) for attr in orm_model.inputs],
            output=TypeDef.model_validate(orm_model.output),
            body=[ast_stmt_adapter.validate_python(s) for s in orm_model.body],
        )

    @classmethod
    def _attr_to_domain(cls, orm_model: AttributeModel) -> Attribute:
        value = (
            expr_def_adapter.validate_python(orm_model.value)
            if orm_model.value
            else None
        )
        _type = (
            TypeDef.model_validate(orm_model.type_def) if orm_model.type_def else None
        )
        return Attribute(
            id=AttributeId.reconstitute(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            type=_type,
            value=value,
        )

    @classmethod
    def to_orm(cls, domain_entity: Component) -> ComponentModel:
        match domain_entity.kind:
            case ComponentKind.CLASS:
                return cls._class_to_orm(domain_entity)
            case ComponentKind.UNION:
                return cls._union_to_orm(domain_entity)
            case _:
                raise ValueError(f"Unknown component kind: {domain_entity.kind}")

    @classmethod
    def _class_to_orm(cls, domain_entity: ClassComponent) -> ClassComponentModel:
        component_id_val = domain_entity.id
        return ClassComponentModel(
            id=component_id_val.value,
            kind=domain_entity.kind.value,
            type=domain_entity.type.value,
            name=domain_entity.name,
            description=domain_entity.description,
            context=domain_entity.context,
            layer=domain_entity.layer.value,
            bases=[t.model_dump(mode="json") for t in domain_entity.bases],
            attributes=[
                cls._attr_to_orm(attr, component_id=component_id_val)
                for attr in domain_entity.attributes
            ],
            behaviors=[
                cls._behavior_to_orm(beh, component_id=component_id_val)
                for beh in domain_entity.behaviors
            ],
        )

    @classmethod
    def _union_to_orm(cls, domain_entity: UnionComponent) -> UnionComponentModel:
        return UnionComponentModel(
            id=domain_entity.id.value,
            kind=domain_entity.kind.value,
            type=domain_entity.type.value,
            name=domain_entity.name,
            description="",
            context=domain_entity.context,
            layer=domain_entity.layer.value,
            discriminator=domain_entity.discriminator,
        )

    @classmethod
    def _behavior_to_orm(
        cls, domain_entity: Behavior, component_id: ComponentId
    ) -> BehaviorModel:
        behavior_id_val = domain_entity.id.value
        return BehaviorModel(
            id=behavior_id_val,
            component_id=component_id.value,
            name=domain_entity.name,
            description=domain_entity.description,
            scenarios=[s.model_dump(mode="json") for s in domain_entity.scenarios],
            output=domain_entity.output.model_dump(mode="json"),
            body=[s.model_dump(mode="json") for s in domain_entity.body],
            inputs=[
                cls._attr_to_orm(attr, behavior_id=domain_entity.id)
                for attr in domain_entity.inputs
            ],
        )

    @classmethod
    def _attr_to_orm(
        cls,
        domain_entity: Attribute,
        component_id: ComponentId | None = None,
        behavior_id: BehaviorId | None = None,
    ) -> AttributeModel:
        value_dict = (
            expr_def_adapter.dump_python(domain_entity.value, mode="json")
            if domain_entity.value
            else None
        )
        type_def = (
            domain_entity.type.model_dump(mode="json") if domain_entity.type else None
        )
        return AttributeModel(
            id=domain_entity.id.value,
            component_id=component_id.value if component_id else None,
            behavior_id=behavior_id.value if behavior_id else None,
            name=domain_entity.name,
            description=domain_entity.description,
            type_def=type_def,
            value=value_dict,
        )
