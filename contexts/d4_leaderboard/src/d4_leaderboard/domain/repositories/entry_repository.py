from abc import ABC
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.domain.aggregates.entry import Entry
from foundation.persistence.ports.repository import Repository


class EntryRepository(Repository[Entry, EntryId], ABC):
    pass
