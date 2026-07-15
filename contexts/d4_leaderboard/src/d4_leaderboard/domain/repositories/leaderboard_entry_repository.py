from d4_leaderboard.domain.aggregates.leaderboard_entry import LeaderboardEntry
from abc import ABC
from d4_leaderboard.domain.identities.leaderboard_entry_id import LeaderboardEntryId
from foundation.persistence.ports.repository import Repository


class LeaderboardEntryRepository(Repository[LeaderboardEntry, LeaderboardEntryId], ABC):
    pass
