"""暗黑破坏神 IV (D4Client) 天梯榜【is_visible 页面检测与 4 次连续缓存对比】手动执行脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点 / 判定条件:
  👉 [功能 2/7: LeaderboardScreen.is_visible 页面状态判定与缓存耗时测试]

本脚本用于对真实窗口连续执行 is_visible() 4 次（每次间隔 0.5 秒），测量真实 OCR 耗时与帧缓存提升：
1. 记录第 1 次冷调用的真实耗时 (ms);
2. 记录第 2、3、4 次暖调用的真实耗时 (ms);
3. 计算耗时提升与缓存加速效果。

日志记录至 logs/verify_is_visible.log。

使用方法:
    # 对默认窗口执行 4 次连续 is_visible 检测 (间隔 0.5s):
    uv run python packages/d4_client/examples/03_verify_is_visible.py

    # 对特定窗口标题执行:
    uv run python packages/d4_client/examples/03_verify_is_visible.py --title "暗黑破坏神IV"
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


async def measure_is_visible_loops(
    screen: LeaderboardScreen, iterations: int = 4, interval_sec: float = 0.5
) -> list[tuple[int, bool, float]]:
    """连续执行 iterations 次 is_visible()，每次间隔 interval_sec 秒，返回 (序号, 结果, 耗时ms) 列表。"""
    records: list[tuple[int, bool, float]] = []

    for i in range(1, iterations + 1):
        t0 = time.perf_counter()
        is_vis = await screen.is_visible()
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        records.append((i, is_vis, elapsed_ms))

        if i < iterations:
            await asyncio.sleep(interval_sec)

    return records


def run_is_visible_verification(title_keyword: str, logger: logging.Logger) -> None:
    logger.info("=" * 75)
    logger.info("开始执行功能 [2/7]: LeaderboardScreen.is_visible (4 次连续真实耗时测试)")
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"配置 title_roi 相对比例: {layout.title_roi}")
    logger.info(f"匹配目标标题文字: '{layout.title_text}'")

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

    real_screen = LeaderboardScreen(window=client.window)
    logger.info(
        f"目标窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height})"
    )
    logger.info("开始执行 4 次连续 is_visible() 检视 (间隔 0.5s)...\n")

    results = asyncio.run(
        measure_is_visible_loops(real_screen, iterations=4, interval_sec=0.5)
    )

    logger.info("---------------------------------------------------------------------------")
    logger.info("📊 连续 4 次 is_visible() 真实执行耗时分析:")
    logger.info("---------------------------------------------------------------------------")

    first_ms = results[0][2]
    for idx, res, ms in results:
        tag = "第 1 次 [冷调用]" if idx == 1 else f"第 {idx} 次 [暖调用 / 0.5s 后]"
        logger.info(
            f"  - {tag}: is_visible() -> {res} | 耗时: {ms:8.2f} ms ({ms / 1000.0:.4f} 秒)"
        )

    if len(results) > 1:
        avg_cached_ms = sum(r[2] for r in results[1:]) / (len(results) - 1)
        saved_ratio = (
            ((first_ms - avg_cached_ms) / first_ms) * 100.0 if first_ms > 0 else 0.0
        )
        logger.info("---------------------------------------------------------------------------")
        logger.info(f"  第 1 次冷调用耗时 : {first_ms:.2f} ms")
        logger.info(f"  后续 3 次平均耗时 : {avg_cached_ms:.2f} ms")
        logger.info(f"  缓存与响应提升   : 节省耗时 {saved_ratio:.1f}%")

    logger.info("=" * 75)
    logger.info("功能 [2/7]: is_visible 检查完毕！日志: logs/verify_is_visible.log")
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.is_visible 真实耗时与缓存对比脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_is_visible",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("is_visible_verify")

    run_is_visible_verification(title_keyword=args.title, logger=logger)


if __name__ == "__main__":
    main()
