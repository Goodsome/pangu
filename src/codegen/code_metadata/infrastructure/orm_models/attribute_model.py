from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from codegen.shared.infrastructure.orm_models.base import BaseORM

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.behavior_model import (
        BehaviorModel,
    )
    from codegen.code_metadata.infrastructure.orm_models.component_model import (
        ClassComponentModel,
    )


class AttributeModel(BaseORM):
    __tablename__: str = "attributes"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    component_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), index=True, nullable=True
    )
    behavior_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("behaviors.id", ondelete="CASCADE"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    type_def: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    component: Mapped[ClassComponentModel | None] = relationship(
        "ClassComponentModel", back_populates="attributes", foreign_keys=[component_id]
    )
    behavior: Mapped[BehaviorModel | None] = relationship(
        "BehaviorModel", back_populates="inputs", foreign_keys=[behavior_id]
    )
