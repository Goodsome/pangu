# -*- coding: utf-8 -*-
"""示例 4: 向梦幻西游窗口 1 发送 OCR 文字识别测试 (04_verify_ocr.py)。

说明：
    检测窗口 1 (索引 0) 的指定 ROI 区域画面，
    保存完整客户区截图至 logs/ocr_debug_full.png，
    保存实际捕获的 ROI 区域截图至 logs/ocr_debug_region.png 供人工查验比对，
    进行 OCR 画面分析，并清晰打印出识别到的文本信息、置信度与坐标位置。

运行方式：
    uv run python packages/mhxy_client/examples/04_verify_ocr.py
"""

import asyncio
import ctypes
import logging
import sys
from pathlib import Path

pkg_src = Path(__file__).resolve().parent.parent / "src"
if str(pkg_src) not in sys.path:
    sys.path.insert(0, str(pkg_src))

from mhxy_client import (  # noqa: E402
    RelativeRegion,
    create_mhxy_client_by_index,
)

# 开启物理 1:1 High-DPI 感知，防止 Windows DPI 缩放导致像素与坐标漂移
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

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
logger = logging.getLogger("mhxy_client.verify_ocr")


async def async_main() -> None:
    logger.info("=" * 70)
    logger.info("  [MHXY Client] 示例 4: OCR 文字识别测试 (窗口 #1 - 指定 ROI 区域)")
    logger.info("=" * 70)

    # 1. 实例化窗口 1 客户端并装载 OCR 引擎
    client = create_mhxy_client_by_index(0, init_cv_engines=True)

    # 2. 定义检测区域 (例如屏幕右侧区域: RelativeRegion(x=0.7, y=0.2, w=0.3, h=0.6))
    target_roi = RelativeRegion(x=0.7, y=0.2, width=0.3, height=0.6)
    abs_roi = target_roi.to_absolute(client.window.width, client.window.height)

    logger.info(f"  * 目标窗口 HWND : {client.hwnd} ({hex(client.hwnd)})")
    logger.info(f"  * 目标窗口标题 : {client.title}")
    logger.info(f"  * 窗口客户区尺寸: {client.window.width} x {client.window.height}")
    logger.info(f"  * 检测目标区域  : {target_roi} -> {abs_roi}")

    # 3. 保存全图与局部切片图供对比校验
    full_path = log_dir / "ocr_debug_full.png"
    region_path = log_dir / "ocr_debug_region.png"

    logger.info("\n[Vision] 正在捕获窗口全图与目标 ROI 区域画面...")

    async with client:
        # A. 捕获完整客户区全图画面并保存
        full_frame = await client.capture(region=None)
        if full_frame.mat is not None:
            full_frame.save(full_path)
            logger.info(
                f"[Save] 📷 窗口客户区【全图】截图已保存至: {full_path.as_uri()} ({full_frame.width}x{full_frame.height})"
            )

        # B. 捕获指定 ROI 区域单帧并保存
        region_frame = await client.capture(region=target_roi)
        if region_frame.mat is not None:
            region_frame.save(region_path)
            logger.info(
                f"[Save] 📷 目标 ROI 【切片】截图已保存至: {region_path.as_uri()} ({region_frame.width}x{region_frame.height})"
            )

        # C. 运行 OCR 识别
        results = await client.ocr(confidence_threshold=0.5, roi=target_roi)

        if results:
            logger.info(f"\n[OK] 在指定区域共识别到 {len(results)} 条文本:\n")
            print("-" * 70)
            for idx, item in enumerate(results, 1):
                msg = (
                    f"  #{idx:02d} | 文本: '{item.text}' "
                    f"| 置信度: {item.confidence:.2f} "
                    f"| 中心坐标: {item.center} "
                    f"| 范围: {item.rect}"
                )
                logger.info(msg)
            print("-" * 70)
        else:
            logger.info("[Info] 指定区域未检索到符合条件的文本。")

    logger.info("=" * 70)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
