import json
from dataclasses import dataclass
from typing import override
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.ports.outbox_repository import OutboxRepository
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jOutboxRepository(OutboxRepository):
    session: Neo4jSession

    @override
    def save(self, message: IntegrationEvent) -> None:
        payload = message.model_dump(mode="json")
        event_type = type(message).__name__
        query = "CREATE (o:OutboxMessage { event_type: $event_type, payload: $payload, created_at: timestamp() })"
        self.session.execute(query, event_type=event_type, payload=json.dumps(payload))
