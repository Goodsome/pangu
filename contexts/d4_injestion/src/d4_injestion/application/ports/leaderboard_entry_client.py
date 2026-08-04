"""榜单 Entry 注入客户端端口：通过 HTTP 将记录推送到 d4_leaderboard。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord


class LeaderboardEntryClient(ABC):
    """d4_leaderboard Entry 注入客户端端口 (HTTP)。"""

    @abstractmethod
    async def create_entry(self, record: LeaderboardRecord) -> None:
        """通过 HTTP POST /entries/ 创建一条榜单记录。

        Args:
            record: 待注入的单条榜单记录。
        """
        ...

    @abstractmethod
    async def aclose(self) -> None:
        """释放底层 HTTP 连接资源。"""
        ...
