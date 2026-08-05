# -*- coding: utf-8 -*-
"""示例 2: 向梦幻西游窗口 1 发送鼠标点击事件 (02_verify_mouse_click.py)。

说明：
    对窗口 1 (索引 0) 发送鼠标左键点击。

运行方式：
    uv run python packages/mhxy_client/examples/02_verify_mouse_click.py
"""

import asyncio
import logging
import sys
from pathlib import Path
from client_core import Point
from sys_input import MouseButton
from mhxy_client import (  # noqa: E402
    create_mhxy_client_by_index,
)

# 配置日志保存至根目录 logs/mhxy_client.log
log_dir = Path(__file__).resolve().parent.parent.parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "mhxy_client.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("mhxy_client.verify_mouse")


async def async_main() -> None:
    logger.info("=" * 60)
    logger.info("  [MHXY Client] 示例 2: 全局 SendInput 鼠标点击测试 (窗口 #1)")
    logger.info("=" * 60)

    # 实例化窗口 1 客户端 (使用全局 SendInput 硬件外设模拟)
    client = create_mhxy_client_by_index(0, use_hardware_input=True)

    # 计算窗口客户区中心坐标作为点击目标
    center_point = Point(x=client.window.width // 2, y=client.window.height // 2)

    logger.info(f"  * 目标窗口 HWND : {client.hwnd} ({hex(client.hwnd)})")
    logger.info(f"  * 目标窗口标题 : {client.title}")
    logger.info(f"  * 窗口客户区尺寸: {client.window.width} x {client.window.height}")
    logger.info(f"  * 拟点击相对位置: {center_point} (客户区中心)")

    logger.info(
        "\n[Input] 正在置顶激活窗口并发送全局物理鼠标点击 (Win32HardwareBackend SendInput)..."
    )

    async with client:
        await client.mouse_click(point=center_point, button=MouseButton.LEFT)
        logger.info("[OK] 全局物理鼠标点击命令执行完毕！")

    logger.info("=" * 60)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
