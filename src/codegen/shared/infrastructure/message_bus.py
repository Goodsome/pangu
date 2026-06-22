from collections.abc import Iterable
import logging
from dataclasses import dataclass
from typing import Protocol
from typing import assert_never
from codegen.shared.application.ports.base_unit_of_work import BaseUnitOfWork
from codegen.shared.domain.core.command import Command
from codegen.shared.domain.core.event import Event

logger = logging.getLogger(__name__)


class CommandHandler[T_Command: Command](Protocol):

    def __call__(self, cmd: T_Command, uow: BaseUnitOfWork) -> None: ...


class EventHanlder(Protocol):

    def __call__(self, event: Event, uow: BaseUnitOfWork) -> Iterable[Command]: ...

@dataclass
class BaseMessageBus:
    uow: BaseUnitOfWork
    command_handlers: dict[type[Command], CommandHandler[Command]]
    event_handlers: dict[type[Event], list[EventHanlder]]

    def handle(self, message: Command | Event) -> None:
        queue = [message]
        with self.uow:
            while queue:
                msg = queue.pop(0)
                match msg:
                    case Command():
                        self._handle_command(msg)
                        for event in self.uow.collect_events():
                            queue.append(event)
                    case Event():
                        for cmd in self._handle_event(msg):
                            queue.append(cmd)
                    case _:
                        assert_never(msg)
            self.uow.commit()

    def _handle_command(self, command: Command) -> None:
        handler = self.command_handlers.get(type(command))
        logger.info(f"Handling {command=}")
        if not handler:
            raise NotImplementedError(f"type(command)={type(command)!r}")
        try:
            handler(command, self.uow)
        except Exception:
            logger.exception(f"Exception handling command {command}")
            raise

    def _handle_event(self, event: Event) -> Iterable[Command]:
        for handler in self.event_handlers.get(type(event), []):
            try:
                logger.info(f"Handling {handler=}")
                yield from handler(event, self.uow)
            except Exception:
                logger.exception(f"Exception handling sync event {event}")
                raise


class MessageBusFactory(Protocol):

    def __call__(self) -> BaseMessageBus:
        ...