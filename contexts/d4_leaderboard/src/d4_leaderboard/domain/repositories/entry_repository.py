from abc import ABC
from foundation.persistence.ports.repository import AsyncRepository
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.identities.entry_id import EntryId


class EntryRepository(AsyncRepository[Entry, EntryId], ABC):
    pass
