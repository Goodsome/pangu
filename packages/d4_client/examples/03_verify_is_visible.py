"""暗黑破坏神 IV (D4Client) 天梯榜【is_visible 缓存与耗时对比】手动执行验证脚本。

对应上层行为树 d4_automation 中 build_leaderboard_capture_tree 节点 / 判定条件:
  👉 [功能 2/7: LeaderboardScreen.is_visible 缓存验证与耗时统计]

本脚本用于连续执行 is_visible() 4 次（每次间隔 0.5 秒），验证帧缓存/识别缓存性能提升：
1. 记录第 1 次冷调用 (未缓存画面/未缓存模型) 的全流程耗时 (ms);
2. 记录第 2、3、4 次暖调用 (间隔 0.5s 后的检视) 耗时 (ms);
3. 自动对比计算耗时降幅，直观展示缓存效果。

日志基于 foundation.logging_setup 记录在 logs/verify_is_visible.log。

使用方法:
    # 1. 默认执行 4 次连续 is_visible 检测 (间隔 0.5s):
    uv run python packages/d4_client/examples/03_verify_is_visible.py

    # 2. 对真实/指定测试窗口验证 (例如记事本、浏览器):
    uv run python packages/d4_client/examples/03_verify_is_visible.py --title "记事本"
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
    """连续执行 iterations 次 is_visible()，每次间隔 interval_sec 秒，返回 (序号, 判定结果, 耗时ms) 列表。"""
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


def run_is_visible_cache_verification(
    title_keyword: str, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info(
        "开始检查功能 [2/7]: LeaderboardScreen.is_visible (4 次连续检测, 间隔 0.5s 缓存性能测试)"
    )
    logger.info("=" * 75)

    layout = LeaderboardLayoutConfig()
    logger.info(f"1. 强类型配置 title_roi: {layout.title_roi}")
    logger.info(f"   匹配目标标题文字: '{layout.title_text}'")

    rects = find_d4_window_rects(title_keyword=title_keyword)

    if not rects:
        logger.info(f"\n2. [提示] 当前未检索到开启的 '{title_keyword}' 真实窗口。")
        logger.info(
            "          请启动游戏或传入 --title \"已打开的窗口名\" (如记事本/浏览器) 运行真实画面的 4 次连续耗时测试。"
        )
        logger.info(
            '          示例: uv run python packages/d4_client/examples/03_verify_is_visible.py --title "记事本"'
        )
    else:
        logger.info(f"\n2. 检索到 {len(rects)} 个目标窗口，建立 D4Client 连接...")
        clients = create_d4_clients(title_keyword=title_keyword)
        client = clients[0]
        screen = LeaderboardScreen(window=client.window)

        logger.info(
            f"   目标窗口 HWND=0x{client.hwnd:X} ({client.window.width}x{client.window.height})"
        )
        logger.info("   开始执行连续 4 次 is_visible() 检视 (每次间隔 0.5 秒)...\n")

        # 运行 4 次异步循环测试
        results = asyncio.run(
            measure_is_visible_loops(screen, iterations=4, interval_sec=0.5)
        )

        logger.info(
            "---------------------------------------------------------------------------"
        )
        logger.info("📊 连续 4 次 is_visible() 执行耗时与缓存性能分析:")
        logger.info(
            "---------------------------------------------------------------------------"
        )

        first_ms = results[0][2]
        for idx, res, ms in results:
            tag = (
                "第 1 次 [冷调用]"
                if idx == 1
                else f"第 {idx} 次 [暖调用 / 间隔 0.5s]"
            )
            logger.info(
                f"  - {tag}: is_visible() -> {res} | 耗时: {ms:8.2f} ms ({ms / 1000.0:.4f} 秒)"
            )

        if len(results) > 1:
            avg_cached_ms = sum(r[2] for r in results[1:]) / (len(results) - 1)
            saved_ratio = (
                ((first_ms - avg_cached_ms) / first_ms) * 100.0
                if first_ms > 0
                else 0.0
            )
            logger.info(
                "---------------------------------------------------------------------------"
            )
            logger.info(f"  第 1 次冷调用耗时 : {first_ms:.2f} ms")
            logger.info(f"  后续 3 次平均耗时 : {avg_cached_ms:.2f} ms")
            logger.info(f"  缓存与响应提升   : 节省耗时 {saved_ratio:.1f}%")

    logger.info("=" * 75)
    logger.info(
        "功能 [2/7]: is_visible 缓存测试完成！完整日志保存至 logs/verify_is_visible.log"
    )
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeaderboardScreen.is_visible 间隔 0.5s 连续 4 次缓存验证脚本"
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

    run_is_visible_cache_verification(title_keyword=args.title, logger=logger)


if __name__ == "__main__":
    main()
