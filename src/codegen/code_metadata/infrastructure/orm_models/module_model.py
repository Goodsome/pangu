from __future__ import annotations
from typing import Any
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from codegen.code_metadata.infrastructure.orm_models.component_v2_model import (
    ComponentV2Model,
)
from codegen.shared.infrastructure.orm_models.base import BaseORM


class ModuleModel(BaseORM):
    __tablename__: str = "modules"
    __mapper_args__ = {"polymorphic_on": "kind"}
    id: Mapped[UUID] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1024), unique=True)
    dir_module_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("modules.id", ondelete="SET NULL"), nullable=True
    )
    components: Mapped[list[ComponentV2Model]] = relationship(
        "ComponentV2Model",
        foreign_keys="[ComponentV2Model.module_id]",
        cascade="all, delete-orphan",
        order_by="ComponentV2Model.position",
        collection_class=ordering_list("position"),
    )
