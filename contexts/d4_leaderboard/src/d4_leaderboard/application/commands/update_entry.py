from dataclasses import dataclass
from datetime import datetime
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.value_objects.equipment import Equipment
from d4_leaderboard.domain.value_objects.paragon import ParagonBoard
from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.talisman import TalismanSnapshot
from foundation.building_blocks.command import Command


class UpdateEntryCommand(Command):
    id: EntryId
    player_name: str | None = None
    player_class: PlayerClass | None = None
    tier: int | None = None
    duration_ms: int | None = None
    occurred_at: datetime | None = None
    equipment: list[Equipment] | None = None
    skills: list[Skill] | None = None
    paragon_boards: list[ParagonBoard] | None = None
    talismans: TalismanSnapshot | None = None


@dataclass
class UpdateEntryCommandHandler:
    async def execute(self, cmd: UpdateEntryCommand, uow: RepoProvider) -> None:
        entry = await uow.entries.get(cmd.id)
        if cmd.player_name is not None:
            entry.player_name = cmd.player_name
        if cmd.player_class is not None:
            entry.player_class = cmd.player_class
        if cmd.tier is not None:
            entry.tier = cmd.tier
        if cmd.duration_ms is not None:
            entry.duration_ms = cmd.duration_ms
        if cmd.occurred_at is not None:
            entry.occurred_at = cmd.occurred_at
        if cmd.equipment is not None:
            entry.equipment = cmd.equipment
        if cmd.skills is not None:
            entry.skills = cmd.skills
        if cmd.paragon_boards is not None:
            entry.paragon_boards = cmd.paragon_boards
        if cmd.talismans is not None:
            entry.talismans = cmd.talismans
        await uow.entries.save(entry)
