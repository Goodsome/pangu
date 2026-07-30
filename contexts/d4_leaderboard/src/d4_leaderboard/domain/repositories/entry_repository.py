from abc import ABC

from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.persistence.ports.repository import AsyncRepository


class EntryRepository(AsyncRepository[Entry, EntryId], ABC): ...
