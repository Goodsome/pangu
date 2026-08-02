from collections.abc import Awaitable, Iterable
import logging
from dataclasses import dataclass
from inspect import isawaitable
from typing import Protocol, assert_never

from foundation.building_blocks.command import Command
from foundation.building_blocks.event import Event
from foundation.persistence.ports.session_manager import (
    AsyncSessionManager,
    SessionManager,
)

logger = logging.getLogger(__name__)


class CommandHandler[T_Command: Command](Protocol):
    def __call__(self, cmd: T_Command, uow: SessionManager) -> None: ...


class EventHanlder(Protocol):
    def __call__(
        self, event: Event, uow: SessionManager
    ) -> Iterable[Command] | None: ...


class AsyncCommandHandler[T_Command: Command](Protocol):
    def __call__(
        self, cmd: T_Command, uow: AsyncSessionManager
    ) -> Awaitable[None] | None: ...


class AsyncEventHandler[T_Event: Event](Protocol):
    def __call__(
        self, event: T_Event, uow: AsyncSessionManager
    ) -> Awaitable[Iterable[Command] | None] | Iterable[Command] | None: ...


@dataclass
class BaseMessageBus:
    uow: SessionManager
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
        logger.info(f"Handling command={command!r}")
        if not handler:
            raise NotImplementedError(f"type(command)={type(command)!r}")
        try:
            handler(command, self.uow)
        except Exception:
            logger.exception(f"Exception handling command {command=}")
            raise

    def _handle_event(self, event: Event) -> Iterable[Command]:
        for handler in self.event_handlers.get(type(event), []):
            try:
                logger.info(f"Handling {handler.__class__=} {event=}")
                yield from (handler(event, self.uow) or [])
            except Exception:
                logger.exception(f"Exception handling sync event {event}")
                raise


@dataclass
class AsyncBaseMessageBus:
    uow: AsyncSessionManager
    command_handlers: dict[type[Command], AsyncCommandHandler[Command]]
    event_handlers: dict[type[Event], list[AsyncEventHandler[Event]]]

    async def handle(self, message: Command | Event) -> None:
        queue = [message]
        async with self.uow:
            while queue:
                msg = queue.pop(0)
                match msg:
                    case Command():
                        await self._handle_command(msg)
                        for event in self.uow.collect_events():
                            queue.append(event)
                    case Event():
                        async for cmd in self._handle_event(msg):
                            queue.append(cmd)
                    case _:
                        assert_never(msg)
            await self.uow.commit()

    async def _handle_command(self, command: Command) -> None:
        handler = self.command_handlers.get(type(command))
        logger.info(f"Handling command={command!r}")
        if not handler:
            raise NotImplementedError(f"type(command)={type(command)!r}")
        try:
            res = handler(command, self.uow)
            if isawaitable(res):
                await res
        except Exception:
            logger.exception(f"Exception handling command {command=}")
            raise

    async def _handle_event(self, event: Event):
        for handler in self.event_handlers.get(type(event), []):
            try:
                logger.info(f"Handling handler={handler!r}")
                res = handler(event, self.uow)
                if isawaitable(res):
                    res = await res
                for cmd in res or []:
                    yield cmd
            except Exception:
                logger.exception(f"Exception handling async event {event}")
                raise


class MessageBusFactory(Protocol):
    def __call__(self) -> BaseMessageBus: ...
