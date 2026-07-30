from dataclasses import dataclass
from typing import override
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.orm.outbox_message_module import OutboxMessageModel
from foundation.persistence.ports.outbox_repository import OutboxRepository
from foundation.persistence.sessions.sqlalchemy_session import SqlAlchemySession


@dataclass
class SqlAlchemyOutboxRepository(OutboxRepository):
    session: SqlAlchemySession

    @override
    def save(self, message: IntegrationEvent) -> None:
        payload = message.model_dump(mode="json")
        record = OutboxMessageModel(event_type=type(message).__name__, payload=payload)
        self.session.add(record)
