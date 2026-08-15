from dataclasses import dataclass
from datetime import datetime
from foundation.message_bus.message_bus import AsyncBaseMessageBus
from d4_leaderboard.application.commands.create_entry import CreateEntryCommand
from d4_leaderboard.application.commands.delete_entry import DeleteEntryCommand
from d4_leaderboard.application.commands.update_entry import UpdateEntryCommand
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import ParagonBoard
from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.talisman import TalismanSnapshot


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
        equipment: list[Equipment] | None = None,
        skills: list[Skill] | None = None,
        paragon_boards: list[ParagonBoard] | None = None,
        talismans: TalismanSnapshot | None = None,
    ) -> None:
        cmd = CreateEntryCommand(
            player_name=player_name,
            player_class=player_class,
            tier=tier,
            duration_ms=duration_ms,
            occurred_at=occurred_at,
            equipment=equipment or [],
            skills=skills or [],
            paragon_boards=paragon_boards or [],
            talismans=talismans,
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
        equipment: list[Equipment] | None = None,
        skills: list[Skill] | None = None,
        paragon_boards: list[ParagonBoard] | None = None,
        talismans: TalismanSnapshot | None = None,
    ) -> None:
        cmd = UpdateEntryCommand(
            id=entry_id,
            player_name=player_name,
            player_class=player_class,
            tier=tier,
            duration_ms=duration_ms,
            occurred_at=occurred_at,
            equipment=equipment,
            skills=skills,
            paragon_boards=paragon_boards,
            talismans=talismans,
        )
        await self.message_bus.handle(cmd)

    async def delete_entry(self, entry_id: EntryId) -> None:
        cmd = DeleteEntryCommand(id=entry_id)
        await self.message_bus.handle(cmd)
