from foundation.building_blocks.command import Command
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from dataclasses import dataclass


class UpdateEntryCommand(Command):
    id: EntryId
    name: str | None = None


@dataclass
class UpdateEntryCommandHandler:
    async def execute(self, cmd: UpdateEntryCommand, uow: RepoProvider) -> None:
        entry = await uow.entries.get(cmd.id)
        if cmd.name is not None:
            entry.name = cmd.name
        await uow.entries.save(entry)
