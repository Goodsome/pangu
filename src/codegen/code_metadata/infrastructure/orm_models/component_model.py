from uuid import UUID
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.orderinglist import ordering_list
from typing import Any
from codegen.shared.infrastructure.orm_models.base import BaseORM
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.attribute_model import (
        AttributeModel,
    )
    from codegen.code_metadata.infrastructure.orm_models.behavior_model import (
        BehaviorModel,
    )


class ComponentModel(BaseORM):
    __tablename__: str = "components"
    __table_args__ = (
        UniqueConstraint("context", "name", name="uq_component_context_name"),
    )
    __mapper_args__ = {"polymorphic_on": "kind"}
    id: Mapped[UUID] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(50), index=True, server_default="class")
    type: Mapped[str] = mapped_column(String(50), index=True)
    context: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    layer: Mapped[str] = mapped_column(String(50), index=True, server_default="unknown")


class UnionComponentModel(ComponentModel):
    __mapper_args__ = {"polymorphic_identity": "union"}
    members: Mapped[list[UUID]] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    discriminator: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ClassComponentModel(ComponentModel):
    __mapper_args__ = {"polymorphic_identity": "class"}
    bases: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    attributes: Mapped[list["AttributeModel"]] = relationship(
        "AttributeModel",
        back_populates="component",
        cascade="all, delete-orphan",
        foreign_keys="[AttributeModel.component_id]",
        order_by="AttributeModel.position",
        collection_class=ordering_list("position"),
    )
    behaviors: Mapped[list["BehaviorModel"]] = relationship(
        "BehaviorModel",
        back_populates="component",
        cascade="all, delete-orphan",
        foreign_keys="[BehaviorModel.component_id]",
        order_by="BehaviorModel.position",
        collection_class=ordering_list("position"),
    )
