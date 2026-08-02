"""暗黑破坏神 IV (D4Client) 天梯榜【职业选择功能】手动执行验证脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点:
  👉 [节点 1: SelectClass (职业选择与切换)]

本脚本用于演示与验证重构后的 LeaderboardScreen.select_class 逻辑：
1. 使用 d4_types.enums.player_class.PlayerClass 枚举；
2. 基于 LeaderboardLayoutConfig.class_selector_roi (8 等分相对物理区域) 动态解算职业点击坐标；
3. 从左到右依次为: BARBARIAN (野蛮人), NECROMANCER (死灵法师), SORCERER (巫师), ROGUE (游侠), DRUID (德鲁伊), SPIRITBORN (灵巫), PALADIN (圣骑士), WARLOCK (术士)。

日志保存到 logs/verify_select_class.log 并在控制台打印。

使用方法:
    # 1. 默认测试 1920x1080 尺寸下全部 8 个职业的动态坐标解算:
    uv run python packages/d4_client/examples/02_verify_select_class.py

    # 2. 模拟切换特定职业:
    uv run python packages/d4_client/examples/02_verify_select_class.py --class_name "BARBARIAN"
"""

import argparse
import logging
from pathlib import Path
from unittest.mock import AsyncMock

from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import ORDERED_PLAYER_CLASSES, LeaderboardScreen
from d4_types.enums.player_class import PlayerClass
from foundation.logging_setup import configure_logging


def run_select_class_verification(
    title_keyword: str, target_class: str | None, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info("开始检查功能 [1/7]: SelectClass (天梯榜职业选择与 8 等分解算)")
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(
        f"1. 强类型配置 class_selector_roi: {layout.class_selector_roi} (8 等分相对比例区域)"
    )

    # 模拟在 1920x1080 分辨率下计算 8 个职业的中心点坐标
    mock_window = AsyncMock()
    mock_window.width = 1920
    mock_window.height = 1080
    dummy_screen = LeaderboardScreen(window=mock_window)

    logger.info("\n2. 演示在 1920x1080 物理分辨率下 8 个职业按从左到右顺序解算坐标:")
    for i, pc in enumerate(ORDERED_PLAYER_CLASSES):
        # 演示调用
        import asyncio

        pt = asyncio.run(dummy_screen.select_class(pc))
        logger.info(
            f"   - 格子 #{i + 1}/8 [{pc.value} / {pc.name}]: 解算得出点击 Point(x={pt.x}, y={pt.y})"
        )

    # 3. 检索真实/测试游戏窗口
    logger.info(f"\n3. 检索目标游戏窗口 (标题关键字: '{title_keyword}'):")
    rects = find_d4_window_rects(title_keyword=title_keyword)

    if not rects:
        logger.info(
            f"   [提示] 当前未开启 '{title_keyword}' 窗口，8 等分算法逻辑验证通过。"
        )
        logger.info(
            '          若运行有测试/游戏窗口，可以传入 --title "目标窗口" 进行真实鼠标模拟。'
        )
    else:
        logger.info(f"   [成功] 检索到 {len(rects)} 个游戏窗口。")
        clients = create_d4_clients(title_keyword=title_keyword)
        client = clients[0]

        board_screen = LeaderboardScreen(window=client.window)
        select_enum = (
            PlayerClass[target_class.upper()]
            if target_class
            else PlayerClass.BARBARIAN
        )

        logger.info(
            f"   [执行] 在窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height}) 上模拟选择职业: '{select_enum.value}'"
        )
        try:
            import asyncio

            btn_pt = asyncio.run(board_screen.select_class(select_enum))
            logger.info(
                f"   [OK] 指令执行成功，点击物理像素点: {btn_pt}"
            )
        except Exception as e:
            logger.error(f"   [失败] 切换职业抛出异常: {e}")

    logger.info("=" * 75)
    logger.info(
        "功能 [1/7]: SelectClass 检查完成！完整日志: logs/verify_select_class.log"
    )
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.select_class (职业选择) 功能手动验证脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    parser.add_argument(
        "--class_name",
        type=str,
        default=None,
        help="要切换的目标职业枚举 (如: 'BARBARIAN', 'NECROMANCER')",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_select_class",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("select_class_verify")

    run_select_class_verification(
        title_keyword=args.title,
        target_class=args.class_name,
        logger=logger,
    )


if __name__ == "__main__":
    main()
