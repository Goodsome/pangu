# -*- coding: utf-8 -*-
"""示例 5: 测试获取 MainHUD 当前地图名称 (05_verify_get_current_map.py)。

说明：
    基于 foundation.configure_logging 配置日志落盘，
    自动获取运行中的梦幻西游游戏窗口，
    通过 client.main_hud 访问 MainHUD 页面对象模型，
    调用 await hud.get_current_map() 解析获取当前地图名称并打印输出。

运行方式：
    uv run python packages/mhxy_client/examples/05_verify_get_current_map.py
"""

import asyncio
import ctypes
import logging
import sys
from pathlib import Path

pkg_src = Path(__file__).resolve().parent.parent / "src"
if str(pkg_src) not in sys.path:
    sys.path.insert(0, str(pkg_src))

from foundation import configure_logging  # noqa: E402
from mhxy_client import (  # noqa: E402
    create_mhxy_client_by_index,
    find_mhxy_window_rects,
)

# 开启物理 1:1 High-DPI 感知
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

log_dir = Path(__file__).resolve().parent.parent.parent.parent / "logs"
configure_logging(app_name="mhxy_client", log_dir=log_dir, log_level=logging.INFO)
logger = logging.getLogger("mhxy_client.get_current_map")


async def async_main() -> None:
    logger.info("=" * 70)
    logger.info("  [MHXY Client] 示例 5: MainHUD 获取当前地图名称测试")
    logger.info("=" * 70)

    rects = find_mhxy_window_rects(title_keyword="梦幻")
    if not rects:
        logger.warning(
            "❌ 未识别到运行中的梦幻西游窗口，请确保游戏运行并处于可见状态。"
        )
        return

    client = create_mhxy_client_by_index(0, init_cv_engines=True)
    logger.info(f"  * 目标窗口 HWND : {client.hwnd} ({hex(client.hwnd)})")
    logger.info(f"  * 目标窗口标题 : {client.title}")
    logger.info(f"  * 窗口分辨率   : {client.window.width} x {client.window.height}")

    async with client:
        logger.info("\n[HUD] 正在调用 client.main_hud.get_current_map()...")
        hud = client.main_hud

        is_vis = await hud.is_visible()
        logger.info(f"  * MainHUD 界面可见状态: {is_vis}")

        map_name = await hud.get_current_map()
        if map_name:
            logger.info(f"🎉 成功识别当前地图名称: 【 {map_name} 】")
        else:
            logger.warning(
                "⚠️ 未能解析识别出地图名称 (请检查地图区域 ROI 是否已被标定或是否有遮挡)。"
            )

    logger.info("=" * 70)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
