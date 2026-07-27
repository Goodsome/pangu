from foundation.persistence.orm.base import BaseORM
from sqlalchemy.orm import Mapped
from uuid import UUID
from sqlalchemy.orm import mapped_column


class EntryModel(BaseORM):
    __tablename__: str = "entries"
    id: Mapped[UUID] = mapped_column(primary_key=True)
