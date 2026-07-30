from abc import ABC, abstractmethod


class BaseSession(ABC):
    """统一持久化 Session 抽象接口"""

    @abstractmethod
    def commit(self) -> None:
        """提交当前事务"""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """回滚当前事务"""
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭当前会话"""
        pass


class AsyncBaseSession(ABC):
    """统一异步持久化 Session 抽象接口"""

    @abstractmethod
    async def commit(self) -> None:
        """提交当前事务"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """回滚当前事务"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭当前会话"""
        pass
