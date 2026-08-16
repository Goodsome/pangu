from abc import ABC, abstractmethod

from d4_leaderboard.application.dtos.affix_distribution_dto import AffixDistributionDto
from d4_leaderboard.application.dtos.affix_distribution_filter import (
    AffixDistributionFilter,
)
from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.application.dtos.entry_filter import EntryFilter
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.common_types.page import Page, PageQuery


class EntryQueryService(ABC):
    @abstractmethod
    async def get(self, id: EntryId) -> EntryDto: ...

    @abstractmethod
    async def find_by_query(self, query: PageQuery[EntryFilter]) -> Page[EntryDto]: ...

    @abstractmethod
    async def get_affix_distribution(
        self, condition: AffixDistributionFilter
    ) -> AffixDistributionDto: ...
