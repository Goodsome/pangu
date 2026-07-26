"""查找暗黑破坏神游戏窗口，获取第 0 个窗口，截图并进行全图 OCR 识别脚本。"""

import asyncio
import logging
from pathlib import Path

import cv2
import numpy as np

from d4_client import (
    create_d4_client_by_index,
    find_d4_window_rects,
    sort_window_rects,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def draw_grid_10x10(image: np.ndarray) -> np.ndarray:
    """在图像副本上绘制 10x10 网格线及百分比刻度标注。"""
    grid_img = image.copy()
    h, w = grid_img.shape[:2]

    # 1. 绘制 X 轴 10 等份垂直网格线
    for i in range(1, 10):
        x = int(w * i / 10)
        # 黑色双边加亮青色主线，确保在任何背景下极度清晰
        cv2.line(grid_img, (x, 0), (x, h), (0, 0, 0), 3)
        cv2.line(grid_img, (x, 0), (x, h), (255, 255, 0), 1)

        text = f"{i * 10}%"
        cv2.putText(
            grid_img, text, (x + 4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2
        )
        cv2.putText(
            grid_img,
            text,
            (x + 4, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 255),
            1,
        )

    # 2. 绘制 Y 轴 10 等份水平网格线
    for i in range(1, 10):
        y = int(h * i / 10)
        cv2.line(grid_img, (0, y), (w, y), (0, 0, 0), 3)
        cv2.line(grid_img, (0, y), (w, y), (255, 255, 0), 1)

        text = f"{i * 10}%"
        cv2.putText(
            grid_img, text, (8, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2
        )
        cv2.putText(
            grid_img,
            text,
            (8, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 255),
            1,
        )

    return grid_img


async def main() -> None:
    print("🔍 正在查找系统中的暗黑破坏神游戏窗口...")

    # 支持中文及英文标题匹配
    rects = find_d4_window_rects(title_keyword="暗黑破坏神IV")
    if not rects:
        rects = find_d4_window_rects(title_keyword="Diablo IV")
    if not rects:
        rects = find_d4_window_rects(title_keyword="暗黑破坏神")

    if not rects:
        print("❌ 未找到运行中的暗黑破坏神游戏窗口！请确保游戏已被启动且窗口可见。")
        return

    sorted_rects = sort_window_rects(rects)
    target_win = sorted_rects[0]

    print(
        f"✅ 共找到 {len(sorted_rects)} 个游戏窗口。选择第 0 个窗口:\n"
        f"   - 句柄 (HWND): {target_win.hwnd}\n"
        f"   - 窗口位置: Left={target_win.left}, Top={target_win.top}\n"
        f"   - 客户区尺寸: {target_win.width}x{target_win.height}"
    )

    # 创建第 0 个窗口对应的 D4Client 客户端
    d4_client = create_d4_client_by_index(index=0)

    async with d4_client:
        print("\n📸 正在捕获游戏窗口画面...")
        await d4_client.begin_frame()
        frame = await d4_client.window.capture()

        # 保存原始截图和 10x10 网格标注截图
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # 1. 原始截图
        raw_save_path = output_dir / "d4_capture_screenshot.png"
        cv2.imwrite(str(raw_save_path), frame.mat)
        print(f"💾 原始截图已保存至: {raw_save_path.resolve()}")

        # 2. 10x10 网格线标注截图
        grid_mat = draw_grid_10x10(frame.mat)
        grid_save_path = output_dir / "d4_capture_screenshot_grid.png"
        cv2.imwrite(str(grid_save_path), grid_mat)
        print(f"📐 10x10 网格线截图已保存至: {grid_save_path.resolve()}")

        print("\n🔍 正在进行 OCR 文字识别...")
        results = await d4_client.window.ocr(confidence_threshold=0.5)

        print(f"\n✨ OCR 识别完成！共找到 {len(results)} 条文本:\n" + "=" * 70)
        for idx, res in enumerate(results, start=1):
            print(
                f"[{idx:02d}] 置信度: {res.confidence:.2f} | "
                f'文本: "{res.text}" | '
                f"中心坐标: ({res.center.x}, {res.center.y}) | "
                f"区域: {res.rect}"
            )
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
