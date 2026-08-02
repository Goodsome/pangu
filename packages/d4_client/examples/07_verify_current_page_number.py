"""暗黑破坏神 IV (D4Client) 天梯榜【current_page_number 页码识别与耗时统计】手动执行脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点 / 判定条件:
  👉 [功能 6/7: LeaderboardScreen.current_page_number 页码 OCR 识别与页码解析]

本脚本用于对真实窗口执行 current_page_number()，测量 OCR 页码识别效果与耗时：
1. 依据 LeaderboardLayoutConfig.page_number_roi (相对比例区域: x=0.5104, y=0.8766, width=0.0381, height=0.0301);
2. 捕获画面并调用 OCR 识别 "N/M" 格式文字并解析分子页码；
3. 显式记录并打印执行总耗时 (精确至毫秒 ms)。

日志记录至 logs/verify_current_page_number.log。

使用方法:
    # 默认对目标窗口识别页码并打点记录耗时:
    uv run python packages/d4_client/examples/07_verify_current_page_number.py

    # 针对指定窗口标题并连续检测 4 次 (间隔 0.5 秒):
    uv run python packages/d4_client/examples/07_verify_current_page_number.py --title "暗黑破坏神IV" --loops 4
"""

import argparse
import asyncio
import logging
from pathlib import Path
import time

from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import LeaderboardScreen
from foundation.logging_setup import configure_logging


async def measure_current_page_number_loops(
    screen: LeaderboardScreen, iterations: int = 1, interval_sec: float = 0.5
) -> list[tuple[int, int | None, float]]:
    """连续执行 iterations 次 current_page_number()，每次间隔 interval_sec 秒，返回 (序号, 页码结果, 耗时ms) 列表。"""
    records: list[tuple[int, int | None, float]] = []

    for i in range(1, iterations + 1):
        t0 = time.perf_counter()
        page_num = await screen.current_page_number()
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        records.append((i, page_num, elapsed_ms))

        if i < iterations:
            await asyncio.sleep(interval_sec)

    return records


def run_current_page_number_verification(
    title_keyword: str, loops: int, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info(
        f"开始执行功能 [6/7]: LeaderboardScreen.current_page_number (页码 OCR 识别与耗时统计, 循环 {loops} 次)"
    )
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"配置 page_number_roi 相对比例: {layout.page_number_roi}")

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
        f"目标窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height})"
    )
    logger.info(f"正在执行 current_page_number() 真实 OCR 识别 (共 {loops} 次)...\n")

    results = asyncio.run(
        measure_current_page_number_loops(board_screen, iterations=loops, interval_sec=0.5)
    )

    logger.info("---------------------------------------------------------------------------")
    logger.info("📊 current_page_number() 真实执行耗时与识别页码分析:")
    logger.info("---------------------------------------------------------------------------")

    first_ms = results[0][2]
    for idx, page_val, ms in results:
        res_str = f"第 {page_val} 页" if page_val is not None else "未识别到页码 (None)"
        tag = "第 1 次 [冷调用]" if idx == 1 else f"第 {idx} 次 [暖调用 / 0.5s 后]"
        logger.info(
            f"  - {tag}: 结果={res_str:15s} | 耗时: {ms:8.2f} ms ({ms / 1000.0:.4f} 秒)"
        )

    if len(results) > 1:
        avg_cached_ms = sum(r[2] for r in results[1:]) / (len(results) - 1)
        saved_ratio = (
            ((first_ms - avg_cached_ms) / first_ms) * 100.0 if first_ms > 0 else 0.0
        )
        logger.info("---------------------------------------------------------------------------")
        logger.info(f"  第 1 次冷调用耗时 : {first_ms:.2f} ms")
        logger.info(f"  后续平均耗时     : {avg_cached_ms:.2f} ms")
        logger.info(f"  缓存与响应提升   : 节省耗时 {saved_ratio:.1f}%")

    logger.info("=" * 75)
    logger.info(
        "功能 [6/7]: current_page_number 完毕！日志: logs/verify_current_page_number.log"
    )
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.current_page_number 页码识别与耗时统计脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    parser.add_argument(
        "--loops",
        type=int,
        default=1,
        help="连续测量的次数 (默认 1 次，可传 4 次对比缓存)，每次间隔 0.5 秒",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_current_page_number",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("current_page_number_verify")

    run_current_page_number_verification(
        title_keyword=args.title,
        loops=args.loops,
        logger=logger,
    )


if __name__ == "__main__":
    main()
