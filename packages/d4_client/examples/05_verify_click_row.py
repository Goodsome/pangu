"""暗黑破坏神 IV (D4Client) 天梯榜【click_row 榜单行点击功能】手动执行验证脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点 / 动作:
  👉 [功能 4/7: LeaderboardScreen.click_row 榜单行 10 等分解算与点击]

本脚本用于手动执行 LeaderboardScreen.click_row 功能：
1. 依据 LeaderboardLayoutConfig.records_roi (相对比例区域: x=0.3377, y=0.3882, width=0.4248, height=0.3992);
2. 垂直按 10 等分求得每行中心物理坐标点；
3. 执行真实的鼠标移动与点击。

日志记录至 logs/verify_click_row.log。

使用方法:
    # 默认解算第 1 行 (row_index=0) 并执行点击:
    uv run python packages/d4_client/examples/05_verify_click_row.py

    # 点击指定行 (如第 5 行 row_index=4):
    uv run python packages/d4_client/examples/05_verify_click_row.py --row 4
"""

import argparse
import asyncio
import logging
from pathlib import Path

from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import LeaderboardScreen
from foundation.logging_setup import configure_logging


def run_click_row_verification(
    title_keyword: str, row_index: int, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info(
        f"开始执行功能 [4/7]: LeaderboardScreen.click_row (第 {row_index + 1}/10 行点击)"
    )
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"配置 records_roi 相对比例: {layout.records_roi}")

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
        f"正在对窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height}) 执行 click_row(row_index={row_index})..."
    )

    try:
        click_pt = asyncio.run(board_screen.click_row(row_index))
        logger.info(
            f"[成功] 点击第 {row_index + 1} 行指令执行完成，10 等分算得物理像素点: Point(x={click_pt.x}, y={click_pt.y})"
        )
    except Exception as e:
        logger.error(f"[失败] 点击行号抛出异常: {e}")

    logger.info("=" * 75)
    logger.info("功能 [4/7]: click_row 完毕！日志: logs/verify_click_row.log")
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.click_row 榜单行点击手动验证脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    parser.add_argument(
        "--row",
        type=int,
        default=0,
        help="要点击的行索引 (0-9，对应第 1-10 名，默认 0)",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_click_row",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("click_row_verify")

    run_click_row_verification(
        title_keyword=args.title,
        row_index=args.row,
        logger=logger,
    )


if __name__ == "__main__":
    main()
