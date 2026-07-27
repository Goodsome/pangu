from foundation.building_blocks.command import Command
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.application.ports.unit_of_work import UnitOfWork
from dataclasses import dataclass


class DeleteEntryCommand(Command):
    id: EntryId


@dataclass
class DeleteEntryCommandHandler:
    def execute(self, cmd: DeleteEntryCommand, uow: UnitOfWork) -> None:
        entry = uow.entries.get(cmd.id)
        uow.entries.delete(entry)
