from datetime import datetime
from uuid import UUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from d4_leaderboard.domain.enums.player_class import PlayerClass
from foundation.persistence.orm.base import BaseORM


class EntryModel(BaseORM):
    __tablename__: str = "entries"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    player_name: Mapped[str] = mapped_column()
    player_class: Mapped[PlayerClass] = mapped_column(
        SQLEnum(PlayerClass, native_enum=False),
    )
    tier: Mapped[int] = mapped_column()
    duration_ms: Mapped[int] = mapped_column()
    occurred_at: Mapped[datetime] = mapped_column()
