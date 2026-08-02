"""快捷标定天梯榜 (LeaderboardScreen) 相对 ROI 的辅助脚本 (支持增量标定模式)。

使用说明:
1. 保证游戏运行并处于天梯榜界面。
2. 运行脚本: uv run python packages/d4_client/scripts/calibrate_leaderboard_roi.py
3. 脚本会自动读取 LeaderboardLayoutConfig 的现有配置:
   - 若 `title_roi` / `class_selector_roi` / `records_roi` 已配置，自动跳过。
   - 仅对未配置 (默认空值) 的字段依次弹窗提示鼠标拖拽框选。
4. 标定完成后，控制台将输出完整的增量 RelativeRegion 配置片段。
"""

import asyncio
import logging

from d4_client import (
    create_d4_client_by_index,
    find_d4_window_rects,
    sort_window_rects,
)
from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_client.models import RelativeRegion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_relative_roi(roi: RelativeRegion | None) -> bool:
    """检查 RelativeRegion 是否为有效配置 (宽度和高度均大于 0)。"""
    if roi is None:
        return False
    return roi.width > 0.0 and roi.height > 0.0


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

    # 1. 加载当前既有 LeaderboardLayoutConfig
    current_config = LeaderboardLayoutConfig()
    print("\n📋 检查既有 LeaderboardLayoutConfig 配置状态 (增量模式):")

    target_fields = [
        ("title_roi", "标题区域 (如 '天梯榜')"),
        ("class_selector_roi", "职业选择图标栏区域"),
        ("records_roi", "榜单记录整体10行区域"),
        ("view_config_roi", "'查看配置'按钮/弹出菜单区域"),
        ("next_page_roi", "'下一页' 按钮/翻页区域"),
        ("previous_page_roi", "'上一页' 按钮/翻页区域"),
        ("page_number_roi", "页码区域"),
    ]

    final_rois: dict[str, RelativeRegion | None] = {}
    need_calibrate: list[tuple[str, str]] = []

    for field_name, desc in target_fields:
        existing_val: RelativeRegion = getattr(
            current_config, field_name, RelativeRegion()
        )
        if is_valid_relative_roi(existing_val):
            print(f"  - ⚡ [{field_name}] 已有有效配置: {existing_val} (自动跳过)")
            final_rois[field_name] = existing_val
        else:
            print(f"  - 📌 [{field_name}] 未配置 ({desc})，等待标定")
            need_calibrate.append((field_name, desc))

    # 2. 对未配置的字段进行交互式拖拽标定
    if need_calibrate:
        d4_client = create_d4_client_by_index(index=0)
        async with d4_client:
            print("\n📸 正在捕获游戏窗口画面...")
            await d4_client.begin_frame()
            frame = await d4_client.window.capture()

            total = len(need_calibrate)
            for idx, (field_name, desc) in enumerate(need_calibrate, start=1):
                print("\n" + "=" * 60)
                print(f"🖱️ 步骤 {idx}/{total}: 请框选 [{field_name}] ({desc})")
                print("   - 按 ENTER / SPACE 确认框选")
                print("   - 按 ESC 或 c 取消框选")
                print("=" * 60)

                window_title = f"[{idx}/{total}] Select {field_name} (Press ENTER/SPACE to confirm)"
                roi = await d4_client.window.select_relative_roi(
                    window_name=window_title,
                    image=frame,
                )
                final_rois[field_name] = roi
    else:
        print("\n✨ 所有 ROI 字段均已在 config 中配置完成，无需额外标定！")

    # 3. 控制台格式化输出最新配置片段
    print("\n" + "=" * 70)
    print("🎉 标定/汇总完成！生成的 LeaderboardLayoutConfig 代码如下：")
    print("=" * 70)
    print("from dataclasses import dataclass")
    print("from d4_client.models import RelativeRegion\n")
    print("@dataclass(frozen=True)")
    print("class LeaderboardLayoutConfig:")

    for field_name, desc in target_fields:
        val = final_rois.get(field_name)
        if is_valid_relative_roi(val):
            assert val is not None
            print(
                f"    {field_name}: RelativeRegion = RelativeRegion("
                f"x={val.x:.4f}, y={val.y:.4f}, "
                f"width={val.width:.4f}, height={val.height:.4f})"
            )
        else:
            print(f"    # {field_name}: 未配置 ({desc})")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
