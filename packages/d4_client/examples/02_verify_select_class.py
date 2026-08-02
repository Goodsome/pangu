"""暗黑破坏神 IV (D4Client) 天梯榜【职业选择功能】手动执行验证脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点:
  👉 [功能 1/7: LeaderboardScreen.select_class (职业选择与 8 等分解算)]

本脚本用于手动执行 LeaderboardScreen.select_class 功能：
1. 传入 d4_types.enums.player_class.PlayerClass 枚举对象；
2. 依据 LeaderboardLayoutConfig.class_selector_roi (8 等分相对比例) 动态解算对应物理像素坐标；
3. 执行真实的鼠标移动与点击切换。

日志记录至 logs/verify_select_class.log。

使用方法:
    # 默认切换至 BARBARIAN (野蛮人):
    uv run python packages/d4_client/examples/02_verify_select_class.py

    # 切换指定职业 (如 NECROMANCER):
    uv run python packages/d4_client/examples/02_verify_select_class.py --class_name "NECROMANCER"
"""

import argparse
import asyncio
import logging
from pathlib import Path

from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import LeaderboardScreen
from d4_types.enums.player_class import PlayerClass
from foundation.logging_setup import configure_logging


def run_select_class_verification(
    title_keyword: str, target_class: str, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info("开始执行功能 [1/7]: SelectClass (天梯榜职业选择与 8 等分解算)")
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"配置 class_selector_roi 相对比例: {layout.class_selector_roi}")

    try:
        select_enum = PlayerClass[target_class.upper()]
    except KeyError:
        logger.error(
            f"[错误] 未知的职业枚举 '{target_class}'。可用枚举: {[c.name for c in PlayerClass]}"
        )
        logger.info("=" * 75)
        return

    # 检索真实目标窗口
    rects = find_d4_window_rects(title_keyword=title_keyword)
    if not rects:
        logger.warning(
            f"[未找到窗口] 当前未开启标题包含 '{title_keyword}' 的窗口。"
        )
        logger.info(
            '             请开启游戏或传入 --title "目标窗口" (如 "记事本") 后重新运行。'
        )
        logger.info("=" * 75)
        return

    logger.info(f"检索到 {len(rects)} 个目标窗口，正在建立 D4Client 连接...")
    clients = create_d4_clients(title_keyword=title_keyword)
    client = clients[0]

    board_screen = LeaderboardScreen(window=client.window)
    logger.info(
        f"正在对窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height}) 执行职业选择 → {select_enum.name} ({select_enum.value})..."
    )

    try:
        btn_pt = asyncio.run(board_screen.select_class(select_enum))
        logger.info(
            f"[成功] 切换职业指令执行完成，解算并点击物理像素点: Point(x={btn_pt.x}, y={btn_pt.y})"
        )
    except Exception as e:
        logger.error(f"[失败] 切换职业抛出异常: {e}")

    logger.info("=" * 75)
    logger.info("功能 [1/7]: SelectClass 完毕！日志: logs/verify_select_class.log")
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.select_class 手动执行脚本"
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
        default="BARBARIAN",
        help="要切换的目标职业枚举 (默认: 'BARBARIAN'，如: 'NECROMANCER', 'SORCERER')",
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
