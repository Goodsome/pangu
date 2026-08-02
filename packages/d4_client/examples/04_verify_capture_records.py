"""暗黑破坏神 IV (D4Client) 天梯榜【capture_records_region 记录区域截图功能】手动执行验证脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点 / 动作:
  👉 [功能 3/7: LeaderboardScreen.capture_records_region 榜单记录截图与落盘]

本脚本用于手动执行 capture_records_region 真实抓图与落盘：
1. 依据 LeaderboardLayoutConfig.records_roi (相对比例区域: x=0.3377, y=0.3882, width=0.4248, height=0.3992);
2. 捕获当前游戏/测试窗口画面；
3. 将截取的榜单 10 条记录保存为本地 PNG 文件 (只接受 Path 对象)。

日志记录至 logs/verify_capture_records.log。

使用方法:
    # 执行截图并保存到默认路径 (packages/d4_client/screenshots/leaderboard_records.png):
    uv run python packages/d4_client/examples/04_verify_capture_records.py

    # 指定保存文件路径与目标窗口标题:
    uv run python packages/d4_client/examples/04_verify_capture_records.py --title "暗黑破坏神IV" --output "packages/d4_client/screenshots/my_records.png"
"""

import argparse
import asyncio
import logging
from pathlib import Path

from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import LeaderboardScreen
from foundation.logging_setup import configure_logging


def run_capture_records_verification(
    title_keyword: str, output_path: Path, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info("开始执行功能 [3/7]: LeaderboardScreen.capture_records_region (记录区域截图落盘)")
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"配置 records_roi 相对比例: {layout.records_roi}")
    logger.info(f"目标保存 Path: {output_path.resolve()}")

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
        f"正在对窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height}) 截取记录区域..."
    )

    try:
        saved_file = asyncio.run(board_screen.capture_records_region(output_path))
        logger.info(f"[成功] 记录区域截图已成功保存至磁盘 → {saved_file.resolve()}")
    except Exception as e:
        logger.error(f"[失败] 截图落盘抛出异常: {e}")

    logger.info("=" * 75)
    logger.info("功能 [3/7]: capture_records_region 完毕！日志: logs/verify_capture_records.log")
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.capture_records_region 手动截图验证脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="screenshots/leaderboard_records.png",
        help="图片落盘输出文件路径 (默认: 'screenshots/leaderboard_records.png')",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_capture_records",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("capture_records_verify")

    run_capture_records_verification(
        title_keyword=args.title,
        output_path=Path(args.output),
        logger=logger,
    )


if __name__ == "__main__":
    main()
