from collections.abc import Iterable, Sequence
from typing import Any, TypeVar, override
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession as RawAsyncSession
from sqlalchemy.orm import Session as RawSession
from foundation.persistence.ports.base_session import AsyncBaseSession, BaseSession

T = TypeVar("T")


class SqlAlchemySession(BaseSession):
    """SQLAlchemy Session 显式强类型包装类"""

    _raw_session: RawSession

    def __init__(self, raw_session: RawSession) -> None:
        self._raw_session = raw_session

    @property
    def raw_session(self) -> RawSession:
        return self._raw_session

    @override
    def commit(self) -> None:
        self._raw_session.commit()

    @override
    def rollback(self) -> None:
        self._raw_session.rollback()

    @override
    def close(self) -> None:
        self._raw_session.close()

    def flush(self, objects: Sequence[Any] | None = None) -> None:
        self._raw_session.flush(objects)

    def add(self, instance: Any) -> None:
        self._raw_session.add(instance)

    def add_all(self, instances: Iterable[Any]) -> None:
        self._raw_session.add_all(instances)

    def delete(self, instance: Any) -> None:
        self._raw_session.delete(instance)

    def get(
        self,
        entity: type[T],
        ident: Any,
        **kwargs: Any,
    ) -> T | None:
        return self._raw_session.get(entity, ident, **kwargs)

    def merge(self, instance: T, load: bool = True, options: Any = None) -> T:
        return self._raw_session.merge(instance, load=load, options=options)

    def execute(self, statement: Executable, params: Any = None, **kw: Any) -> Any:
        return self._raw_session.execute(statement, params=params, **kw)

    def scalar(self, statement: Executable, params: Any = None, **kw: Any) -> Any:
        return self._raw_session.scalar(statement, params=params, **kw)

    def scalars(self, statement: Executable, params: Any = None, **kw: Any) -> Any:
        return self._raw_session.scalars(statement, params=params, **kw)


class AsyncSqlAlchemySession(AsyncBaseSession):
    """SQLAlchemy AsyncSession 显式强类型包装类"""

    _raw_session: RawAsyncSession

    def __init__(self, raw_session: RawAsyncSession) -> None:
        self._raw_session = raw_session

    @property
    def raw_session(self) -> RawAsyncSession:
        return self._raw_session

    @override
    async def commit(self) -> None:
        await self._raw_session.commit()

    @override
    async def rollback(self) -> None:
        await self._raw_session.rollback()

    @override
    async def close(self) -> None:
        await self._raw_session.close()

    async def flush(self, objects: Sequence[Any] | None = None) -> None:
        await self._raw_session.flush(objects)

    def add(self, instance: Any) -> None:
        self._raw_session.add(instance)

    def add_all(self, instances: Iterable[Any]) -> None:
        self._raw_session.add_all(instances)

    async def delete(self, instance: Any) -> None:
        await self._raw_session.delete(instance)

    async def get(
        self,
        entity: type[T],
        ident: Any,
        **kwargs: Any,
    ) -> T | None:
        return await self._raw_session.get(entity, ident, **kwargs)

    async def merge(self, instance: T, load: bool = True, options: Any = None) -> T:
        return await self._raw_session.merge(instance, load=load, options=options)

    async def execute(
        self, statement: Executable, params: Any = None, **kw: Any
    ) -> Any:
        return await self._raw_session.execute(statement, params=params, **kw)

    async def scalar(
        self, statement: Executable, params: Any = None, **kw: Any
    ) -> Any:
        return await self._raw_session.scalar(statement, params=params, **kw)

    async def scalars(
        self, statement: Executable, params: Any = None, **kw: Any
    ) -> Any:
        return await self._raw_session.scalars(statement, params=params, **kw)
