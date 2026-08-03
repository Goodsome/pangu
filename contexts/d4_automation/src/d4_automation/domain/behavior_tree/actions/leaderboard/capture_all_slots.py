"""Action: 遍历玩家配置页所有槽位（装备/技能/巅峰/护身符），逐一悬停截图保存。"""

import asyncio
import logging
from dataclasses import dataclass
from typing import override

from d4_automation.config import load_capture_task_config
from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.core import BaseNode
from d4_automation.domain.enums.node_status import NodeStatus
from d4_automation.infrastructure.image_io import save_image
from d4_client import ImageFrame, PlayerConfigScreen

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
                cfg = load_capture_task_config()
                rank_dir = blackboard.leaderboard.rank_output_dir()
                hover_delay = cfg.timing.after_hover_slot

                # 1. 装备槽位采集 (直接使用 screen 持有的绝对状态与解算)
                eq_count = screen.get_equipment_slot_count()

                for i in range(eq_count):
                    save_path = await screen.capture_equipment_slot(
                        output_dir=rank_dir,
                        slot_index=i,
                    )
                    await asyncio.sleep(hover_delay)
                    logger.debug(
                        "[CaptureAllSlots] 排名 %d | equipment[%d] → %s",
                        blackboard.leaderboard.current_rank,
                        i,
                        save_path,
                    )

                # 2. 技能槽位采集 (使用 LeaderboardLayoutConfig 相对比例区域解算)
                sk_count = screen.get_skill_slot_count()

                for i in range(sk_count):
                    save_path = await screen.capture_skill_slot(
                        output_dir=rank_dir,
                        slot_index=i,
                    )
                    await asyncio.sleep(hover_delay)
                    logger.debug(
                        "[CaptureAllSlots] 排名 %d | skill[%d] → %s",
                        blackboard.leaderboard.current_rank,
                        i,
                        save_path,
                    )

                # 3. 护身符槽位采集 (1排7个，使用 LeaderboardLayoutConfig 相对比例区域解算)
                tm_count = screen.get_talisman_slot_count()

                for i in range(tm_count):
                    save_path = await screen.capture_talisman_slot(
                        output_dir=rank_dir,
                        slot_index=i,
                    )
                    await asyncio.sleep(hover_delay)
                    logger.debug(
                        "[CaptureAllSlots] 排名 %d | talisman[%d] → %s",
                        blackboard.leaderboard.current_rank,
                        i,
                        save_path,
                    )

                # 4. 其它槽位采集任务 (paragon)
                slot_tasks = [
                    (
                        "paragon",
                        screen.paragon_slot_count,
                        screen.capture_paragon_slot,
                        screen.paragon_slot_name,
                    ),
                ]

                for slot_type, count, capture_fn, name_fn in slot_tasks:
                    for i in range(count):
                        slot_name = name_fn(i)
                        frame: ImageFrame = await capture_fn(i)
                        await asyncio.sleep(hover_delay)

                        save_path = rank_dir / f"{slot_type}_{slot_name}.png"
                        await save_image(frame, save_path)
                        logger.debug(
                            "[CaptureAllSlots] 排名 %d | %s[%d] '%s' → %s",
                            blackboard.leaderboard.current_rank,
                            slot_type,
                            i,
                            slot_name,
                            save_path,
                        )

                logger.info(
                    "[CaptureAllSlots] 排名 %d 全部槽位截图完成",
                    blackboard.leaderboard.current_rank,
                )
                return NodeStatus.SUCCESS
            case _:
                logger.warning("[CaptureAllSlots] 当前面板非 PlayerConfigScreen，跳过")
                return NodeStatus.FAILURE
