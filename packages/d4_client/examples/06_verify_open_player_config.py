"""暗黑破坏神 IV (D4Client) 天梯榜【open_player_config 查看配置界面入口】手动执行验证脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点 / 动作:
  👉 [功能 5/7: LeaderboardScreen.open_player_config 点击查看配置并进入 PlayerConfigScreen]

本脚本用于手动执行 LeaderboardScreen.open_player_config 功能：
1. 依据 LeaderboardLayoutConfig.view_config_roi (相对比例区域) 动态解算其中心物理像素点；
2. 执行鼠标点击，返回 PlayerConfigScreen 实例。

日志记录至 logs/verify_open_player_config.log。

使用方法:
    # 默认触发 open_player_config:
    uv run python packages/d4_client/examples/06_verify_open_player_config.py

    # 针对特定窗口标题执行:
    uv run python packages/d4_client/examples/06_verify_open_player_config.py --title "暗黑破坏神IV"
"""

import argparse
import asyncio
import logging
from pathlib import Path

from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import LeaderboardScreen
from foundation.logging_setup import configure_logging


def run_open_player_config_verification(
    title_keyword: str, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info("开始执行功能 [5/7]: LeaderboardScreen.open_player_config (点击'查看配置')")
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"配置 view_config_roi 相对比例: {layout.view_config_roi}")

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
        f"正在对窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height}) 执行 open_player_config()..."
    )

    try:
        player_config_screen = asyncio.run(board_screen.open_player_config())
        logger.info(
            f"[成功] 点击'查看配置'完毕！获取到页面实例: {player_config_screen.__class__.__name__}"
        )
    except Exception as e:
        logger.error(f"[失败] 打开玩家配置页抛出异常: {e}")

    logger.info("=" * 75)
    logger.info(
        "功能 [5/7]: open_player_config 完毕！日志: logs/verify_open_player_config.log"
    )
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.open_player_config 手动执行验证脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_open_player_config",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("open_player_config_verify")

    run_open_player_config_verification(title_keyword=args.title, logger=logger)


if __name__ == "__main__":
    main()
