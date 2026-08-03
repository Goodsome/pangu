"""天梯榜数据采集行为树装配工厂。

使用方式：
    from d4_automation.domain.behavior_tree.leaderboard_capture_tree import build_leaderboard_capture_tree
    from d4_automation.domain.aggregates.blackboard import Blackboard, LeaderboardCaptureContext
    from d4_automation.config import load_capture_task_config

    cfg = load_capture_task_config()
    blackboard = Blackboard(
        client=client,
        current_panel=leaderboard_screen,
        leaderboard=LeaderboardCaptureContext(
            target_end_page=cfg.end_page,
            output_base_dir=cfg.output_dir,
        ),
    )
    tree = build_leaderboard_capture_tree()
    await tree.tick(blackboard)
"""

from d4_automation.domain.behavior_tree.actions.finish import FinishNode
from d4_automation.domain.behavior_tree.actions.leaderboard import (
    CaptureAllSlots,
    CaptureLeaderboardPage,
    ClickRow,
    ClosePlayerConfig,
    GoNextPage,
    OpenPlayerConfig,
    SelectClass,
)
from d4_automation.domain.behavior_tree.conditions.leaderboard import (
    HasMorePages,
    HasMoreRows,
)
from d4_automation.domain.behavior_tree.core import (
    BaseNode,
    RepeatUntilFail,
    Sequence,
)


def build_leaderboard_capture_tree() -> BaseNode:
    """装配完整的天梯榜采集行为树并返回根节点。

    树结构：

    Sequence [总流程]
    ├── SelectClass                      # 切换目标职业
    └── RepeatUntilFail [翻页循环]
        └── Sequence [处理单页]
            ├── HasMorePages             # 条件：还需要采集更多页
            ├── CaptureLeaderboardPage   # 截取整页榜单截图
            ├── RepeatUntilFail [行循环]
            │   └── Sequence [处理单行]
            │       ├── HasMoreRows      # 条件：当前页还有行未处理
            │       ├── ClickRow         # 点击该行触发弹出菜单
            │       ├── OpenPlayerConfig # 进入玩家配置页
            │       ├── CaptureAllSlots  # 遍历所有槽位截图
            │       └── ClosePlayerConfig# 关闭配置页，推进行索引
            └── GoNextPage              # 翻到下一页，推进页码
    """
    single_row_seq = Sequence(
        children=[
            HasMoreRows(),
            ClickRow(),
            OpenPlayerConfig(),
            CaptureAllSlots(),
            ClosePlayerConfig(),
        ]
    )

    row_loop = RepeatUntilFail(child=single_row_seq)

    single_page_seq = Sequence(
        children=[
            HasMorePages(),
            CaptureLeaderboardPage(),
            row_loop,
            GoNextPage(),
        ]
    )

    page_loop = RepeatUntilFail(child=single_page_seq)

    root = Sequence(
        children=[
            SelectClass(),
            page_loop,
            FinishNode(),
        ]
    )

    return root
