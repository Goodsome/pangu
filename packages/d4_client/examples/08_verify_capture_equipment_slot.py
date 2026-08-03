"""暗黑破坏神 IV (PlayerConfigScreen) 装备槽位截图 (capture_equipment_slot) 手动执行验证脚本。

本脚本用于手动执行 PlayerConfigScreen.capture_equipment_slot 功能：
1. 初始化 LeaderboardScreen 状态为野蛮人 (PlayerClass.BARBARIAN), page=1, row=0；
2. 触发 open_player_config() 点击查看配置并自动继承透传状态；
3. 自动计算野蛮人 12 个装备格子及 Tooltip 选区；
4. 逐一悬停并截取保存至执行目录 screenshots/ 下 (保存格式: BARBARIAN_1_0_{slot_index}.png)。

日志记录至 logs/verify_capture_equipment_slot.log。

使用方法:
    # 默认针对游戏窗口执行:
    uv run python packages/d4_client/examples/08_verify_capture_equipment_slot.py

    # 针对特定窗口标题 (如记事本/测试窗口) 执行:
    uv run python packages/d4_client/examples/08_verify_capture_equipment_slot.py --title "无标题 - 记事本"
"""

import argparse
import asyncio
import logging
from pathlib import Path

from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_client.screens.leaderboard import LeaderboardScreen
from d4_types.enums.player_class import PlayerClass
from foundation.logging_setup import configure_logging


def run_capture_equipment_slot_verification(
    title_keyword: str, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info(
        "开始执行功能 [08]: PlayerConfigScreen.capture_equipment_slot 装备截图验证"
    )
    logger.info("=" * 75)

    rects = find_d4_window_rects(title_keyword=title_keyword)
    if not rects:
        logger.warning(f"[未找到窗口] 当前未开启标题包含 '{title_keyword}' 的窗口。")
        logger.info(
            '             请开启游戏或传入 --title "目标窗口" (如 "记事本") 后重新运行。'
        )
        logger.info("=" * 75)
        return

    logger.info(f"检索到 {len(rects)} 个目标窗口，正在建立 D4Client 连接...")
    clients = create_d4_clients(title_keyword=title_keyword, use_hardware_input=False)
    client = clients[0]

    # 置顶并激活窗口，确保全局硬件光标悬停与 Tooltip 正常触发
    client.window.activate()

    # 1. 建立天梯榜屏幕，并记录初始化状态: 野蛮人 (BARBARIAN), page=1, row=0
    board_screen = LeaderboardScreen(
        window=client.window,
        current_class=PlayerClass.BARBARIAN,
        current_page=1,
        current_row=0,
    )
    logger.info(
        f"天梯榜状态初始化完毕: 职业={board_screen.current_class.value}, "
        f"页码={board_screen.current_page}, 行数={board_screen.current_row}"
    )

    async def _execute_capture() -> None:
        # 2. 点击'查看配置'打开配置页，自动透传绑定当前状态
        player_config_screen = await board_screen.open_player_config()
        logger.info(
            f"[成功] 打开玩家配置页 PlayerConfigScreen! "
            f"(绑定状态: 职业={player_config_screen.player_class.value}, "
            f"page={player_config_screen.page}, row={player_config_screen.row})"
        )

        # 3. 保存图片的输出目录: 执行目录 / screenshots
        output_dir = Path.cwd() / "screenshots"
        output_dir.mkdir(parents=True, exist_ok=True)

        eq_count = player_config_screen.get_equipment_slot_count()
        logger.info(
            f"野蛮人装备槽位总数量: {eq_count}，准备逐一悬停截图保存至: {output_dir}"
        )

        for i in range(eq_count):
            save_path = await player_config_screen.capture_equipment_slot(
                output_dir=output_dir,
                slot_index=i,
            )
            logger.info(f"  [装备槽位 {i + 1}/{eq_count}] 截图已保存 → {save_path}")

    try:
        asyncio.run(_execute_capture())
        logger.info("[成功] 野蛮人全部装备槽位截图完成！")
    except Exception as e:
        logger.error(f"[失败] 装备截图过程抛出异常: {e}", exc_info=True)

    logger.info("=" * 75)
    logger.info(
        "功能 [08]: capture_equipment_slot 完毕！日志: logs/verify_capture_equipment_slot.log"
    )
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PlayerConfigScreen.capture_equipment_slot 手动执行验证脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    args = parser.parse_args()

    configure_logging(
        app_name="verify_capture_equipment_slot",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("capture_equipment_slot_verify")

    run_capture_equipment_slot_verification(title_keyword=args.title, logger=logger)


if __name__ == "__main__":
    main()
