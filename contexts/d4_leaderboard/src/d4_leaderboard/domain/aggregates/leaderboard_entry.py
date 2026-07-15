from d4_leaderboard.domain.identities.leaderboard_entry_id import LeaderboardEntryId
from foundation.building_blocks.aggregate_root import AggregateRoot


class LeaderboardEntry(AggregateRoot[LeaderboardEntryId]):
    pass
