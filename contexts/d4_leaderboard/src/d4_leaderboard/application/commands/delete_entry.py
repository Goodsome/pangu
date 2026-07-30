from foundation.building_blocks.command import Command
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from dataclasses import dataclass


class DeleteEntryCommand(Command):
    id: EntryId


@dataclass
class DeleteEntryCommandHandler:
    async def execute(self, cmd: DeleteEntryCommand, uow: RepoProvider) -> None:
        entry = await uow.entries.get(cmd.id)
        await uow.entries.delete(entry)
