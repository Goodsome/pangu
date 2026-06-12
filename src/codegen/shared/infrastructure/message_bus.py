from collections.abc import Iterable
import logging
from dataclasses import dataclass
from typing import Any, Protocol, assert_never

from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command
from codegen.shared.domain.core.event import Event

logger = logging.getLogger(__name__)


class CommandHandler[T_Command: Command, T_UnitOfWork](Protocol):

    def __call__(self, cmd: T_Command, uow: T_UnitOfWork) -> None:
        ...

class EventHanlder[T_Event: Event](Protocol):

    def __call__(self, event: T_Event) -> Iterable[Command]:
        ...

@dataclass
class BaseMessageBus[T: UnitOfWork[Any]]:
    uow: T
    command_handlers: dict[type[Command], CommandHandler[Command, T]]
    sync_event_handlers: dict[type[Event], list[EventHanlder[Event]]]
    # async_event_handlers: dict[type[Event], list[EventHanlder[Event]]]

    def handle(self, message: Command | Event) -> None:
        queue = [message]

        with self.uow:
            while queue:
                msg = queue.pop(0)
                logger.info(f"handle {msg=}")
                match msg:
                    case Command():
                        self._handle_command(msg)
                        for aggregate in self.uow.repository.collect_seens():
                            queue.extend(aggregate.collect_events())
                    case Event():
                        for cmd in self._handle_event(msg):
                            queue.append(cmd)
                    case _:
                        assert_never(msg)
                            
            self.uow.commit()

    def _handle_command(self, command: Command) -> None:
        handler = self.command_handlers.get(type(command))
        if not handler:
            raise NotImplementedError(f"{type(command)=}")

        try:
            handler(command, self.uow)
        except Exception:
            logger.exception(f"Exception handling command {command}")
            raise

        
    def _handle_event(self, event: Event) -> Iterable[Command]:
        for handler in self.sync_event_handlers.get(type(event), []):
            try:
                yield from handler(event)
            except Exception:
                logger.exception(f"Exception handling sync event {event}")
                raise

        # 2. 路由给异步处理器（最终一致性要求 / Outbox 模式）
        # 只要事件类型注册了异步 Handler，或者明确标记为 IntegrationEvent，就落库发件箱
        # requires_async = type(event) in self.async_event_handlers
        # is_integration = isinstance(event, IntegrationEvent)
        # 
        # if requires_async or is_integration:
        #     self.uow.save_outbox_message(event)