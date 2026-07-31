from dataclasses import dataclass

from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.building_blocks.command import Command


class CreateEntryCommand(Command):
    name: str


@dataclass
class CreateEntryCommandHandler:
    async def execute(self, cmd: CreateEntryCommand, uow: RepoProvider) -> None:
        entry = Entry(
            id=EntryId.create(),
            name=cmd.name,
        )
        await uow.entries.add(entry)
