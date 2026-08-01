"""d4_automation 行为树与配置单元测试。"""

from pathlib import Path

from d4_automation.config import load_capture_task_config
from d4_automation.domain.aggregates.blackboard import LeaderboardCaptureContext
from d4_automation.domain.behavior_tree.leaderboard_capture_tree import (
    build_leaderboard_capture_tree,
)
from d4_automation.domain.behavior_tree.core import Sequence


def test_load_capture_task_config():
    cfg = load_capture_task_config()
    assert cfg.player_class == "野蛮人"
    assert cfg.start_page >= 1
    assert cfg.end_page >= cfg.start_page


def test_leaderboard_capture_context_advancement():
    ctx = LeaderboardCaptureContext(
        player_class="野蛮人",
        current_page=1,
        target_end_page=2,
        current_row=0,
        current_rank=1,
        output_base_dir=Path("output/screenshots"),
    )

    assert ctx.has_more_rows is True
    assert ctx.has_more_pages is True

    # 推进 10 行
    for _ in range(10):
        ctx.advance_row()

    assert ctx.has_more_rows is False

    # 翻页
    ctx.advance_page()
    assert ctx.current_page == 2
    assert ctx.current_row == 0
    assert ctx.has_more_rows is True


def test_build_leaderboard_capture_tree():
    tree = build_leaderboard_capture_tree()
    assert isinstance(tree, Sequence)
    assert len(tree.children) == 2
