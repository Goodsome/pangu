"""快捷标定天梯榜 (LeaderboardScreen) 相对 ROI 的辅助脚本。

使用说明:
1. 保证游戏运行并处于天梯榜界面。
2. 运行脚本: uv run python scripts/calibrate_leaderboard_roi.py
3. 在弹出的画面中按照提示使用鼠标拖拽框选:
   - 第 1 步: title_roi (标题区域)
   - 第 2 步: class_selector_roi (职业选择栏区域)
4. 标定完成后，控制台将自动打印可直接复制粘贴到 Python 代码中的 RelativeRegion 配置片段。
"""

import asyncio
import logging
from d4_client import (
    create_d4_client_by_index,
    find_d4_window_rects,
    sort_window_rects,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    print("🔍 正在查找系统中的暗黑破坏神游戏窗口...")
    rects = (
        find_d4_window_rects(title_keyword="暗黑破坏神IV")
        or find_d4_window_rects(title_keyword="Diablo IV")
        or find_d4_window_rects(title_keyword="暗黑破坏神")
    )

    if not rects:
        print("❌ 未找到运行中的暗黑破坏神游戏窗口！请确保游戏已被启动且窗口可见。")
        return

    sorted_rects = sort_window_rects(rects)
    target_win = sorted_rects[0]

    print(
        f"✅ 共找到 {len(sorted_rects)} 个游戏窗口。选择第 0 个窗口:\n"
        f"   - 句柄 (HWND): {target_win.hwnd}\n"
        f"   - 窗口分辨率: {target_win.width}x{target_win.height}"
    )

    d4_client = create_d4_client_by_index(index=0)

    async with d4_client:
        print("\n📸 正在捕获游戏窗口画面...")
        await d4_client.begin_frame()
        frame = await d4_client.window.capture()

        print("\n============================================================")
        print("🖱️ 步骤 1/2: 请框选 [title_roi] (标题区域，如 '天梯榜')")
        print("   - 按 ENTER / SPACE 确认框选")
        print("   - 按 ESC 或 c 取消框选")
        print("============================================================")
        title_roi = await d4_client.window.select_relative_roi(
            window_name="[1/2] Select title_roi (Press ENTER/SPACE to confirm)",
            image=frame,
        )

        print("\n============================================================")
        print("🖱️ 步骤 2/2: 请框选 [class_selector_roi] (职业选择图标栏区域)")
        print("   - 按 ENTER / SPACE 确认框选")
        print("   - 按 ESC 或 c 取消框选")
        print("============================================================")
        class_selector_roi = await d4_client.window.select_relative_roi(
            window_name="[2/2] Select class_selector_roi (Press ENTER/SPACE to confirm)",
            image=frame,
        )

        print("\n" + "=" * 70)
        print("🎉 标定完成！生成的 Python 代码片段如下：")
        print("=" * 70)
        print("from dataclasses import dataclass")
        print("from d4_client.models import RelativeRegion\n")
        print("@dataclass")
        print("class LeaderboardLayoutConfig:")

        if title_roi:
            print(
                f"    title_roi: RelativeRegion = RelativeRegion("
                f"x={title_roi.x:.4f}, y={title_roi.y:.4f}, "
                f"width={title_roi.width:.4f}, height={title_roi.height:.4f})"
            )
        else:
            print("    # title_roi: 未框选 (已取消)")

        if class_selector_roi:
            print(
                f"    class_selector_roi: RelativeRegion = RelativeRegion("
                f"x={class_selector_roi.x:.4f}, y={class_selector_roi.y:.4f}, "
                f"width={class_selector_roi.width:.4f}, height={class_selector_roi.height:.4f})"
            )
        else:
            print("    # class_selector_roi: 未框选 (已取消)")

        print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
