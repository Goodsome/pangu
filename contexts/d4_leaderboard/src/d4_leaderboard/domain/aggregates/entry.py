from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.building_blocks.aggregate_root import AggregateRoot


class Entry(AggregateRoot[EntryId]):
    pass
