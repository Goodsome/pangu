from dataclasses import dataclass

from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.application.mappers.entry_dto_to_entry import entry_dto_to_entry
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from foundation.building_blocks.command import Command


class CreateEntryCommand(Command):
    dto: EntryDto


@dataclass
class CreateEntryCommandHandler:
    async def execute(self, cmd: CreateEntryCommand, uow: RepoProvider) -> None:
        entry = entry_dto_to_entry(cmd.dto)
        await uow.entries.add(entry)
