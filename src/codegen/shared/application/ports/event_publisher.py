from abc import ABC
from abc import abstractmethod
from event_hub import DomainEvent


class EventPublisher(ABC):
    """Abstract port for publishing domain events."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass
