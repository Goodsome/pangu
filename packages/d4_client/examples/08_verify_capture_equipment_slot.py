"""暗黑破坏神 IV (PlayerConfigScreen) 装备与技能槽位截图手动执行验证脚本。

本脚本用于手动执行 PlayerConfigScreen 槽位截图功能：
1. 初始化 LeaderboardScreen 状态为野蛮人 (PlayerClass.BARBARIAN), page=1, row=0；
2. 触发 open_player_config() 点击查看配置并自动继承透传状态；
3. 支持指定仅测试技能、仅测试装备或测试全部槽位；
4. 点击槽位并截取保存至执行目录 screenshots/ 下。

使用方法:
    # 1. 快捷开关: 仅测试技能截图:
    uv run python packages/d4_client/examples/08_verify_capture_equipment_slot.py --skills-only

    # 2. 快捷开关: 仅测试装备截图:
    uv run python packages/d4_client/examples/08_verify_capture_equipment_slot.py --equipments-only

    # 3. 参数形式指定技能:
    uv run python packages/d4_client/examples/08_verify_capture_equipment_slot.py --target skill

    # 4. 默认执行全部 (装备 + 技能):
    uv run python packages/d4_client/examples/08_verify_capture_equipment_slot.py
"""

import argparse
import asyncio
import logging
from pathlib import Path

from d4_client import PlayerConfigScreen
from d4_client.factory import create_d4_clients, find_d4_window_rects
from d4_types.enums.player_class import PlayerClass
from foundation.logging_setup import configure_logging


def run_capture_verification(
    title_keyword: str, target: str, logger: logging.Logger
) -> None:
    logger.info("=" * 75)
    logger.info(f"开始执行功能 [08]: PlayerConfigScreen 截图验证 (测试目标: {target})")
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

    client.window.activate()

    player_config_screen = PlayerConfigScreen(
        window=client.window,
        player_class=PlayerClass.BARBARIAN,
        page=1,
        row=0,
    )

    async def _execute_capture() -> None:
        # 2. 点击'查看配置'打开配置页，自动透传绑定当前状态
        logger.info(
            f"[成功] 打开玩家配置页 PlayerConfigScreen! "
            f"(绑定状态: 职业={player_config_screen.player_class.value}, "
            f"page={player_config_screen.page}, row={player_config_screen.row})"
        )

        # 3. 保存图片的输出目录: 执行目录 / screenshots
        output_dir = Path.cwd() / "screenshots"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 装备槽位测试
        if target in ("all", "equipment"):
            eq_count = player_config_screen.get_equipment_slot_count()
            logger.info(
                f"野蛮人装备槽位总数量: {eq_count}，准备逐一点击截图保存至: {output_dir}"
            )
            for i in range(eq_count):
                save_path = await player_config_screen.capture_equipment_slot(
                    output_dir=output_dir,
                    slot_index=i,
                )
                logger.info(f"  [装备槽位 {i + 1}/{eq_count}] 截图已保存 → {save_path}")

        # 技能槽位测试
        if target in ("all", "skill"):
            sk_count = player_config_screen.get_skill_slot_count()
            logger.info(
                f"技能槽位总数量: {sk_count}，准备逐一点击截图保存至: {output_dir}"
            )
            for i in range(sk_count):
                save_path = await player_config_screen.capture_skill_slot(
                    output_dir=output_dir,
                    slot_index=i,
                )
                logger.info(f"  [技能槽位 {i + 1}/{sk_count}] 截图已保存 → {save_path}")

        # 护身符槽位测试
        if target in ("all", "talisman"):
            tm_count = player_config_screen.get_talisman_slot_count()
            logger.info(
                f"护身符槽位总数量: {tm_count}，准备逐一点击截图保存至: {output_dir}"
            )
            for i in range(tm_count):
                save_path = await player_config_screen.capture_talisman_slot(
                    output_dir=output_dir,
                    slot_index=i,
                )
                logger.info(
                    f"  [护身符槽位 {i + 1}/{tm_count}] 截图已保存 → {save_path}"
                )

    try:
        asyncio.run(_execute_capture())
        logger.info(f"[成功] 目标 [{target}] 槽位截图处理完成！")
    except Exception as e:
        logger.error(f"[失败] 截图处理过程抛出异常: {e}", exc_info=True)

    logger.info("=" * 75)
    logger.info("功能 [08]: 槽位截图完毕！日志: logs/verify_capture_equipment_slot.log")
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PlayerConfigScreen 槽位截图手动执行验证脚本"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    parser.add_argument(
        "--target",
        type=str,
        choices=["all", "equipment", "skill", "talisman"],
        default="all",
        help="截图测试目标: all (全部), equipment (仅装备), skill (仅技能), talisman (仅护身符)。默认: all",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="快捷开关: 仅测试技能截图 (等同于 --target skill)",
    )
    parser.add_argument(
        "--equipments-only",
        action="store_true",
        help="快捷开关: 仅测试装备截图 (等同于 --target equipment)",
    )
    parser.add_argument(
        "--talisman-only",
        action="store_true",
        help="快捷开关: 仅测试护身符截图 (等同于 --target talisman)",
    )

    args = parser.parse_args()

    # 解析控制开关
    target = args.target
    if args.skills_only:
        target = "skill"
    elif args.equipments_only:
        target = "equipment"
    elif args.talisman_only:
        target = "talisman"

    configure_logging(
        app_name="verify_capture_equipment_slot",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("capture_slot_verify")

    run_capture_verification(title_keyword=args.title, target=target, logger=logger)


if __name__ == "__main__":
    main()
