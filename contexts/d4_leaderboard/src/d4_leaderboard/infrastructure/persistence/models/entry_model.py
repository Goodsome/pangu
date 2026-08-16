from datetime import datetime
from typing import Any
from uuid import UUID
from sqlalchemy import DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from d4_types.enums.player_class import PlayerClass
from foundation.persistence.orm.base import BaseORM


class EntryModel(BaseORM):
    __tablename__: str = "entries"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    player_name: Mapped[str] = mapped_column()
    player_class: Mapped[PlayerClass] = mapped_column(
        SQLEnum(
            PlayerClass,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        )
    )
    tier: Mapped[int] = mapped_column()
    duration_ms: Mapped[int] = mapped_column()
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    skills: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    # 由 skills 派生的 build 签名 (排序 codename 以 '+' 拼接), 无技能时为 NULL
    skill_build_key: Mapped[str | None] = mapped_column(index=True, nullable=True)
    paragon_boards: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB, nullable=True
    )
    talismans: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    equipments: Mapped[list[Any]] = relationship(
        "EntryEquipmentModel",
        back_populates="entry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
