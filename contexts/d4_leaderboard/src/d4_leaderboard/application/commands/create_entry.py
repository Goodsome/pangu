from dataclasses import dataclass
from datetime import datetime
from pydantic import Field
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import ParagonBoard
from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.talisman import TalismanSnapshot
from foundation.building_blocks.command import Command


class CreateEntryCommand(Command):
    player_name: str
    player_class: PlayerClass
    tier: int
    duration_ms: int
    occurred_at: datetime
    equipment: list[Equipment] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    paragon_boards: list[ParagonBoard] = Field(default_factory=list)
    talismans: TalismanSnapshot | None = Field(default=None)


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
            equipment=cmd.equipment,
            skills=cmd.skills,
            paragon_boards=cmd.paragon_boards,
            talismans=cmd.talismans,
        )
        await uow.entries.add(entry)
