from dataclasses import dataclass

from d4_leaderboard.application.commands.create_entry import CreateEntryCommand
from d4_leaderboard.application.commands.delete_entry import DeleteEntryCommand
from d4_leaderboard.application.commands.update_entry import UpdateEntryCommand
from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.message_bus.message_bus import AsyncBaseMessageBus


@dataclass
class D4LeaderboardApi:
    message_bus: AsyncBaseMessageBus

    async def create_entry(self, dto: EntryDto) -> None:
        cmd = CreateEntryCommand(name=dto.name)
        await self.message_bus.handle(cmd)

    async def update_entry(self, entry_id: EntryId, dto: EntryDto) -> None:
        cmd = UpdateEntryCommand(id=entry_id, name=dto.name)
        await self.message_bus.handle(cmd)

    async def delete_entry(self, entry_id: EntryId) -> None:
        cmd = DeleteEntryCommand(id=entry_id)
        await self.message_bus.handle(cmd)
