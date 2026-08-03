"""Action: 遍历玩家配置页所有槽位（装备/技能/巅峰/护身符），逐一悬停截图保存。"""

import logging
from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import PlayerConfigScreen

logger = logging.getLogger(__name__)


@dataclass
class CaptureAllSlots(BaseNode):
    """遍历当前玩家配置页的全部槽位分类，逐一悬停截图。

    截图保存路径：{rank_output_dir}/{slot_type}_{slot_name}.png
      - slot_type: equipment / skill / paragon / amulet

    前置条件：blackboard.current_panel 为 PlayerConfigScreen。
    副作用：无（不修改黑板状态）。
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        match blackboard.current_panel:
            case PlayerConfigScreen() as screen:
                row_dir =  blackboard.leaderboard.output_base_dir
                eq_count = screen.get_equipment_slot_count()

                for i in range(eq_count):
                    await screen.capture_equipment_slot(
                        output_dir=row_dir,
                        slot_index=i,
                    )

                sk_count = screen.get_skill_slot_count()
                for i in range(sk_count):
                    await screen.capture_skill_slot(
                        output_dir=row_dir,
                        slot_index=i,
                    )

                tm_count = screen.get_talisman_slot_count()

                for i in range(tm_count):
                    await screen.capture_talisman_slot(
                        output_dir=row_dir,
                        slot_index=i,
                    )

                return NodeStatus.SUCCESS
            case _:
                logger.warning("[CaptureAllSlots] 当前面板非 PlayerConfigScreen，跳过")
                return NodeStatus.FAILURE
