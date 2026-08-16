from dataclasses import dataclass
from typing import override

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from d4_leaderboard.application.dtos.affix_distribution_dto import (
    AffixDistributionDto,
    AffixDistributionItem,
)
from d4_leaderboard.application.dtos.affix_distribution_filter import (
    AffixDistributionFilter,
)
from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.application.dtos.entry_filter import EntryFilter
from d4_leaderboard.application.ports.entry_query_service import EntryQueryService
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.mappers.entry_mapper import (
    entry_model_to_entry_dto,
)
from d4_leaderboard.infrastructure.persistence.models.entry_equipment_model import (
    EntryEquipmentModel,
)
from d4_leaderboard.infrastructure.persistence.models.entry_equipment_statline_model import (  # noqa: E501
    EntryEquipmentStatlineModel,
)
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel
from foundation.common_types.page import Page, PageQuery


@dataclass
class SqlAlchemyEntryQueryService(EntryQueryService):
    session_factory: async_sessionmaker[AsyncSession]

    @override
    async def get(self, id: EntryId) -> EntryDto:
        async with self.session_factory() as session:
            model = await session.get(EntryModel, id.value)
            if not model:
                raise ValueError(f"Entry {id} not found")
            return entry_model_to_entry_dto(model)

    @override
    async def find_by_query(self, query: PageQuery[EntryFilter]) -> Page[EntryDto]:
        async with self.session_factory() as session:
            conditions = []
            if query.condition.player_class is not None:
                conditions.append(
                    EntryModel.player_class == query.condition.player_class
                )

            count_stmt = select(func.count()).select_from(EntryModel).where(*conditions)
            total_res = await session.execute(count_stmt)
            total: int = total_res.scalar_one() or 0

            # 榜单固定语义：层数高者靠前，同层用时短者靠前，仍相同按时间早者靠前
            stmt = (
                select(EntryModel)
                .where(*conditions)
                .order_by(
                    EntryModel.tier.desc(),
                    EntryModel.duration_ms.asc(),
                    EntryModel.occurred_at.asc(),
                )
            )
            if query.size is not None and query.size > 0:
                offset = (query.current - 1) * query.size
                stmt = stmt.offset(offset).limit(query.size)

            res = await session.execute(stmt)
            models = res.scalars().all()

            items = [entry_model_to_entry_dto(m) for m in models]

            return Page[EntryDto](
                items=items,
                total=total,
                current=query.current,
                size=query.size,
            )

    @override
    async def get_affix_distribution(
        self, condition: AffixDistributionFilter
    ) -> AffixDistributionDto:
        async with self.session_factory() as session:
            entry_conditions = []
            if condition.player_class is not None:
                entry_conditions.append(
                    EntryModel.player_class == condition.player_class
                )
            if condition.min_tier > 1:
                entry_conditions.append(EntryModel.tier >= condition.min_tier)

            equipment_conditions = []
            if condition.slot is not None:
                equipment_conditions.append(
                    EntryEquipmentModel.slot == int(condition.slot)
                )

            # 词缀按 回火/嬗变/自带 三类互斥分组, 精炼 (is_masterwork_crit)
            # 可点在任意词缀上, 故额外按 FILTER 单独计数
            stat = EntryEquipmentStatlineModel
            category = case(
                (stat.is_temper, "temper"),
                (stat.is_transfigured, "transfigured"),
                else_="innate",
            )

            dist_stmt = (
                select(
                    category.label("category"),
                    stat.codename.label("codename"),
                    stat.stat_type.label("stat_type"),
                    func.count().label("affix_count"),
                    func.count()
                    .filter(stat.is_masterwork_crit)
                    .label("masterwork_count"),
                )
                .select_from(EntryModel)
                .join(
                    EntryEquipmentModel, EntryEquipmentModel.entry_id == EntryModel.id
                )
                .join(stat, stat.equipment_id == EntryEquipmentModel.id)
                .where(*entry_conditions, *equipment_conditions)
                .group_by(category, stat.codename, stat.stat_type)
            )

            # 分母: 命中条目数、命中装备件数、带精炼标记的装备件数
            entry_count_stmt = (
                select(func.count()).select_from(EntryModel).where(*entry_conditions)
            )
            item_count_stmt = (
                select(func.count())
                .select_from(EntryEquipmentModel)
                .join(EntryModel, EntryEquipmentModel.entry_id == EntryModel.id)
                .where(*entry_conditions, *equipment_conditions)
            )
            masterwork_item_count_stmt = (
                select(func.count(func.distinct(EntryEquipmentModel.id)))
                .select_from(EntryModel)
                .join(
                    EntryEquipmentModel, EntryEquipmentModel.entry_id == EntryModel.id
                )
                .join(stat, stat.equipment_id == EntryEquipmentModel.id)
                .where(
                    *entry_conditions,
                    *equipment_conditions,
                    stat.is_masterwork_crit,
                )
            )

            entry_count = (await session.execute(entry_count_stmt)).scalar_one() or 0
            item_count = (await session.execute(item_count_stmt)).scalar_one() or 0
            masterwork_item_count = (
                await session.execute(masterwork_item_count_stmt)
            ).scalar_one() or 0
            dist_res = await session.execute(dist_stmt)
            rows = dist_res.all()

            buckets: dict[str, list[AffixDistributionItem]] = {
                "innate": [],
                "temper": [],
                "transfigured": [],
            }
            masterwork: list[AffixDistributionItem] = []

            for row in rows:
                buckets[str(row.category)].append(
                    AffixDistributionItem(
                        codename=row.codename,
                        stat_type=row.stat_type,
                        count=row.affix_count,
                        percentage=_percentage(row.affix_count, item_count),
                    )
                )
                if row.masterwork_count:
                    masterwork.append(
                        AffixDistributionItem(
                            codename=row.codename,
                            stat_type=row.stat_type,
                            count=row.masterwork_count,
                            percentage=_percentage(
                                row.masterwork_count, masterwork_item_count
                            ),
                        )
                    )

            for items in buckets.values():
                items.sort(key=lambda i: i.count, reverse=True)
            masterwork.sort(key=lambda i: i.count, reverse=True)

            return AffixDistributionDto(
                player_class=condition.player_class,
                slot=condition.slot,
                min_tier=condition.min_tier,
                entry_count=entry_count,
                item_count=item_count,
                masterwork_item_count=masterwork_item_count,
                innate=buckets["innate"],
                temper=buckets["temper"],
                transfigured=buckets["transfigured"],
                masterwork_crit=masterwork,
            )


def _percentage(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total * 100, 2)
