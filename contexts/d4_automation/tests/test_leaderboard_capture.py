"""d4_automation 行为树与配置单元测试。"""

from pathlib import Path

from d4_automation.config import load_capture_task_config
from d4_automation.domain.aggregates.blackboard import LeaderboardCaptureContext
from d4_automation.domain.behavior_tree.leaderboard_capture_tree import (
    build_leaderboard_capture_tree,
)
from d4_automation.domain.behavior_tree.core import Sequence


from d4_types.enums.player_class import PlayerClass


def test_load_capture_task_config():
    cfg = load_capture_task_config()
    assert cfg.player_class == PlayerClass.BARBARIAN
    assert cfg.start_page >= 1
    assert cfg.end_page >= cfg.start_page


def test_leaderboard_capture_context_initialization():
    ctx = LeaderboardCaptureContext(
        target_end_page=2,
        output_base_dir=Path("output/screenshots"),
    )
    assert ctx.target_end_page == 2
    assert ctx.output_base_dir == Path("output/screenshots")


def test_build_leaderboard_capture_tree():
    tree = build_leaderboard_capture_tree()
    assert isinstance(tree, Sequence)
    assert len(tree.children) == 2


import pytest


@pytest.mark.anyio
async def test_select_class_node():
    from unittest.mock import AsyncMock, MagicMock
    from d4_automation.domain.aggregates.blackboard import Blackboard
    from d4_automation.domain.behavior_tree.actions.leaderboard.select_class import SelectClass
    from d4_automation.domain.enums.node_status import NodeStatus
    from d4_client import LeaderboardScreen

    mock_screen = MagicMock(spec=LeaderboardScreen)
    mock_screen.select_class = AsyncMock()

    blackboard = Blackboard(
        client=MagicMock(),
        current_panel=mock_screen,
        leaderboard=LeaderboardCaptureContext(
            target_end_page=1,
            output_base_dir=Path("output"),
        ),
    )

    node = SelectClass()
    status = await node.tick(blackboard)

    assert status == NodeStatus.SUCCESS
    mock_screen.select_class.assert_awaited_once_with(PlayerClass.BARBARIAN)


@pytest.mark.anyio
async def test_capture_leaderboard_page_node(tmp_path: Path):
    from unittest.mock import AsyncMock, MagicMock
    from d4_automation.domain.aggregates.blackboard import Blackboard
    from d4_automation.domain.behavior_tree.actions.leaderboard.capture_leaderboard_page import (
        CaptureLeaderboardPage,
    )
    from d4_automation.domain.enums.node_status import NodeStatus
    from d4_client import LeaderboardScreen

    mock_screen = MagicMock(spec=LeaderboardScreen)
    mock_screen.current_class = PlayerClass.BARBARIAN
    mock_screen.current_page = 2
    mock_screen.capture_records_region = AsyncMock()

    ctx = LeaderboardCaptureContext(
        target_end_page=5,
        output_base_dir=tmp_path,
    )
    blackboard = Blackboard(
        client=MagicMock(),
        current_panel=mock_screen,
        leaderboard=ctx,
    )

    node = CaptureLeaderboardPage()
    status = await node.tick(blackboard)

    assert status == NodeStatus.SUCCESS
    expected_path = tmp_path / "BARBARIAN" / "page_002" / "leaderboard_002.png"
    mock_screen.capture_records_region.assert_awaited_once_with(expected_path)


