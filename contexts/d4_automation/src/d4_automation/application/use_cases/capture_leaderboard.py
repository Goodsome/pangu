"""Use Case: 天梯榜数据采集。

负责：
  - 从 capture_task.yaml 读取任务配置初始化 Blackboard
  - 装配并驱动 leaderboard_capture_tree 行为树
  - 管理 D4Client 生命周期
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from d4_automation.config import load_capture_task_config
from d4_automation.domain.aggregates.blackboard import (
    Blackboard,
    LeaderboardCaptureContext,
)
from d4_automation.domain.behavior_tree.leaderboard_capture_tree import (
    build_leaderboard_capture_tree,
)
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import LeaderboardScreen, create_d4_client_by_index


logger = logging.getLogger(__name__)


@dataclass
class CaptureLeaderboard:
    """天梯榜截图采集 Use Case。

    用法::

        use_case = CaptureLeaderboard()
        cancel = asyncio.Event()
        await use_case.execute(window_index=0, cancel_event=cancel)
    """

    async def execute(
        self,
        window_index: int,
        cancel_event: asyncio.Event,  # noqa: ARG002 — Phase 6 中断逻辑时接入
        config_path: Path | None = None,
    ) -> None:
        """执行天梯榜数据采集流程。

        Args:
            window_index: 目标游戏窗口索引（从 0 开始）。
            cancel_event: 外部取消信号，set 后当前页采集完成即退出。
            config_path: 可选的 capture_task.yaml 路径，默认使用内置路径。
        """
        cfg = (
            load_capture_task_config()
            if config_path is None
            else load_capture_task_config(config_path)
        )

        d4_client = create_d4_client_by_index(window_index)

        async with d4_client:
            leaderboard_screen = LeaderboardScreen(window=d4_client.window)

            ctx = LeaderboardCaptureContext(
                player_class=cfg.player_class,
                current_page=cfg.start_page,
                target_end_page=cfg.end_page,
                current_row=0,
                current_rank=(cfg.start_page - 1) * 10 + 1,
                output_base_dir=cfg.output_dir,
            )

            blackboard = Blackboard(
                client=d4_client,
                current_panel=leaderboard_screen,
                leaderboard=ctx,
            )

            tree = build_leaderboard_capture_tree()

            logger.info(
                "[CaptureLeaderboard] 开始采集：职业=%s，页码范围=[%d, %d]，输出目录=%s",
                cfg.player_class,
                cfg.start_page,
                cfg.end_page,
                cfg.output_dir,
            )

            try:
                await d4_client.begin_frame()
                status = await tree.tick(blackboard)

                if status == NodeStatus.SUCCESS:
                    logger.info("[CaptureLeaderboard] 采集完成")
                else:
                    logger.warning(
                        "[CaptureLeaderboard] 行为树以非成功状态结束: %s", status
                    )

            except asyncio.CancelledError:
                logger.info("[CaptureLeaderboard] 收到取消信号，退出")
            except Exception:
                logger.exception("[CaptureLeaderboard] 采集过程中发生未预期异常")
                raise
