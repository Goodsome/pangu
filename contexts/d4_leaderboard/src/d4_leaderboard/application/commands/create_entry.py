from dataclasses import dataclass
from datetime import datetime

from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.building_blocks.command import Command


class CreateEntryCommand(Command):
    player_name: str
    player_class: PlayerClass
    tier: int
    duration_ms: int
    occurred_at: datetime


@dataclass
class CreateEntryCommandHandler:
    async def execute(self, cmd: CreateEntryCommand, uow: RepoProvider) -> None:
        entry = Entry(
            id=EntryId.create(),
            player_name=cmd.player_name,
            player_class=cmd.player_class,
            tier=cmd.tier,
            duration_ms=cmd.duration_ms,
            occurred_at=cmd.occurred_at,
        )
        await uow.entries.add(entry)
