from dataclasses import dataclass
from datetime import datetime
from foundation.message_bus.message_bus import AsyncBaseMessageBus
from d4_leaderboard.application.commands.create_entry import CreateEntryCommand
from d4_leaderboard.application.commands.delete_entry import DeleteEntryCommand
from d4_leaderboard.application.commands.update_entry import UpdateEntryCommand
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId


@dataclass
class D4LeaderboardApi:
    message_bus: AsyncBaseMessageBus

    async def create_entry(
        self,
        player_name: str,
        player_class: PlayerClass,
        tier: int,
        duration_ms: int,
        occurred_at: datetime,
    ) -> None:
        cmd = CreateEntryCommand(
            player_name=player_name,
            player_class=player_class,
            tier=tier,
            duration_ms=duration_ms,
            occurred_at=occurred_at,
        )
        await self.message_bus.handle(cmd)

    async def update_entry(
        self,
        entry_id: EntryId,
        player_name: str | None = None,
        player_class: PlayerClass | None = None,
        tier: int | None = None,
        duration_ms: int | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        cmd = UpdateEntryCommand(
            id=entry_id,
            player_name=player_name,
            player_class=player_class,
            tier=tier,
            duration_ms=duration_ms,
            occurred_at=occurred_at,
        )
        await self.message_bus.handle(cmd)

    async def delete_entry(self, entry_id: EntryId) -> None:
        cmd = DeleteEntryCommand(id=entry_id)
        await self.message_bus.handle(cmd)
