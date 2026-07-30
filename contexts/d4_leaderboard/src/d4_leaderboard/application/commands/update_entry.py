from dataclasses import dataclass

from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.application.mappers.update_entry_from_dto import (
    update_entry_from_dto,
)
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.building_blocks.command import Command


class UpdateEntryCommand(Command):
    id: EntryId
    dto: EntryDto


@dataclass
class UpdateEntryCommandHandler:
    async def execute(self, cmd: UpdateEntryCommand, uow: RepoProvider) -> None:
        entry = await uow.entries.get(cmd.id)
        _ = update_entry_from_dto(entry, cmd.dto)
        await uow.entries.save(entry)
