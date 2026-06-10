from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID
from uuid import uuid4
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from codegen.shared.infrastructure.orm_models.base import BaseORM

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
        CodeNodeModel,
    )


class CodeEdgeModel(BaseORM):
    """统一的关联实体表（图谱边表）"""

    __tablename__: str = "code_edges"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("code_nodes.id", ondelete="CASCADE"), index=True
    )
    target_id: Mapped[UUID] = mapped_column(
        ForeignKey("code_nodes.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(50), index=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    properties: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    source_entity: Mapped[CodeNodeModel] = relationship(
        "CodeNodeModel", foreign_keys=[source_id]
    )
    target_entity: Mapped[CodeNodeModel] = relationship(
        "CodeNodeModel", foreign_keys=[target_id]
    )
    __table_args__ = (
        Index("ix_rel_source_type", "source_id", "type"),
        Index("ix_rel_target_type", "target_id", "type"),
        UniqueConstraint("source_id", "target_id", "type", name="uq_entity_edge"),
    )
