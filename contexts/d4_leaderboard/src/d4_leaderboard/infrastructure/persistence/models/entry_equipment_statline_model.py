from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from foundation.persistence.orm.base import BaseORM


class EntryEquipmentStatlineModel(BaseORM):
    """装备词缀行, entry_equipments.statlines 的规范化拆表"""

    __tablename__: str = "entry_equipment_statlines"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    equipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("entry_equipments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # 保留词缀在装备内的原始顺序
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    affix_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    codename: Mapped[str] = mapped_column(index=True)
    stat_type: Mapped[str] = mapped_column()
    is_greater: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_temper: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_rerolled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_transfigured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_masterwork_crit: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    equipment: Mapped[Any] = relationship(
        "EntryEquipmentModel", back_populates="statlines"
    )
