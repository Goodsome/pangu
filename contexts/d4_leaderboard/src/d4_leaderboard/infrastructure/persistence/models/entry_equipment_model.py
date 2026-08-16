from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from d4_leaderboard.infrastructure.persistence.models.entry_equipment_statline_model import (  # noqa: E501
    EntryEquipmentStatlineModel,
)

from d4_leaderboard.domain.enums.equipment_rarity import EquipmentRarity
from foundation.persistence.orm.base import BaseORM


class EntryEquipmentModel(BaseORM):
    __tablename__: str = "entry_equipments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entry_id: Mapped[UUID] = mapped_column(
        ForeignKey("entries.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    slot: Mapped[int] = mapped_column(index=True)
    item_id: Mapped[int] = mapped_column()
    codename: Mapped[str] = mapped_column()
    base_type: Mapped[str] = mapped_column()
    rarity: Mapped[EquipmentRarity] = mapped_column(
        SQLEnum(
            EquipmentRarity,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        )
    )
    item_power: Mapped[int] = mapped_column()
    is_ancestral: Mapped[bool] = mapped_column(default=False)

    # 词缀已规范化拆表, 其余嵌套类型仍做 JSONB 存储
    statlines: Mapped[list[EntryEquipmentStatlineModel]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=EntryEquipmentStatlineModel.position,
    )
    sockets: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    aspect_power: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    entry: Mapped[Any] = relationship("EntryModel", back_populates="equipments")
