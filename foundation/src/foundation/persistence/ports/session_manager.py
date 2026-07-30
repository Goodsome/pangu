import logging
from abc import ABC
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

from foundation.building_blocks.event import DomainEvent
from foundation.persistence.ports.base_session import AsyncBaseSession, BaseSession

logger = logging.getLogger(__name__)


@dataclass
class SessionManager[TSession: BaseSession = BaseSession](ABC):
    """Session 与事务生命周期管理器"""

    session_factory: Callable[[], TSession]
    _session: TSession | None = field(default=None, init=False)

    @property
    def session(self) -> TSession:
        if self._session is None:
            raise RuntimeError(
                "Session is not active. Use 'with session_manager:' block."
            )
        return self._session

    def __enter__(self) -> Self:
        self._session = self.session_factory()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                self.rollback()
                logger.error(f"Transaction rolled back due to error: {exc_val}")
        finally:
            if self._session is not None:
                try:
                    self._session.close()
                finally:
                    self._session = None

    def commit(self) -> None:
        if self._session is not None:
            self._session.commit()

    def rollback(self) -> None:
        if self._session is not None:
            self._session.rollback()

    def collect_events(self) -> Iterator[DomainEvent]:
        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue
            try:
                attr_val = getattr(self, attr_name)
                if hasattr(attr_val, "collect_events") and callable(
                    getattr(attr_val, "collect_events")
                ):
                    yield from attr_val.collect_events()
            except Exception:
                continue


@dataclass
class AsyncSessionManager[TSession: AsyncBaseSession = AsyncBaseSession](ABC):
    """异步 Session 与事务生命周期管理器"""

    session_factory: Callable[[], TSession]
    _session: TSession | None = field(default=None, init=False)

    @property
    def session(self) -> TSession:
        if self._session is None:
            raise RuntimeError(
                "Session is not active. Use 'async with session_manager:' block."
            )
        return self._session

    async def __aenter__(self) -> Self:
        self._session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
                logger.error(f"Transaction rolled back due to error: {exc_val}")
        finally:
            if self._session is not None:
                try:
                    await self._session.close()
                finally:
                    self._session = None

    async def commit(self) -> None:
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()

    def collect_events(self) -> Iterator[DomainEvent]:
        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue
            try:
                attr_val = getattr(self, attr_name)
                if hasattr(attr_val, "collect_events") and callable(
                    getattr(attr_val, "collect_events")
                ):
                    yield from attr_val.collect_events()
            except Exception:
                continue
