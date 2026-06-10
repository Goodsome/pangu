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
    from codegen.code_metadata.infrastructure.orm_models.attribute_model import (
        AttributeModel,
    )
    from codegen.code_metadata.infrastructure.orm_models.component_model import (
        ClassComponentModel,
    )


class BehaviorModel(BaseORM):
    __tablename__: str = "behaviors"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    component_id: Mapped[UUID] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    scenarios: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    output: Mapped[dict[str, Any]] = mapped_column(JSONB)
    body: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    component: Mapped["ClassComponentModel"] = relationship(back_populates="behaviors")
    inputs: Mapped[list["AttributeModel"]] = relationship(
        "AttributeModel",
        back_populates="behavior",
        cascade="all, delete-orphan",
        foreign_keys="[AttributeModel.behavior_id]",
    )
