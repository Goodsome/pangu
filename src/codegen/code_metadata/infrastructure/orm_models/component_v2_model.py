from __future__ import annotations
from typing import Any
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from codegen.shared.infrastructure.orm_models.base import BaseORM


class ComponentV2Model(BaseORM):
    __tablename__: str = "components_v2"
    __table_args__ = (
        UniqueConstraint("context", "name", name="uq_component_v2_context_name"),
    )
    __mapper_args__ = {"polymorphic_on": "kind"}
    id: Mapped[UUID] = mapped_column(primary_key=True)
    module_id: Mapped[UUID] = mapped_column(
        ForeignKey("modules.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(50), index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    context: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    layer: Mapped[str] = mapped_column(String(50), index=True, server_default="unknown")
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
