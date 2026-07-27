from foundation.persistence.ports.repository import Repository
from d4_leaderboard.domain.identities.entry_id import EntryId
from abc import ABC
from d4_leaderboard.domain.aggregates.entry import Entry


class EntryRepository(Repository[Entry, EntryId], ABC):
    pass
