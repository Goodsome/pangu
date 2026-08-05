"""快捷标定梦幻西游主界面 (MainHUD) 相对 ROI 的辅助脚本 (支持增量标定模式)。

使用说明:
1. 保证梦幻西游游戏运行并处于主界面。
2. 运行脚本: uv run python packages/mhxy_client/scripts/calibrate_main_hud_roi.py
3. 脚本会自动读取 MainHudLayoutConfig 的现有配置:
   - 若 `map_name_roi` / `task_list_roi` 已配置，自动跳过。
   - 仅对未配置 (默认空值) 的字段依次弹窗提示鼠标拖拽框选。
4. 标定完成后，控制台将输出完整的增量 RelativeRegion 配置片段。
"""

import asyncio
import logging

from client_core import RelativeRegion
from mhxy_client import (
    MainHudLayoutConfig,
    create_mhxy_client_by_index,
    find_mhxy_window_rects,
    sort_window_rects,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

target_fields = [
    ("map_name_roi", "地图名称与坐标显示区域"),
    ("task_list_roi", "任务追踪列表区域"),
    ("fu_roi", "任务追踪列表区域"),
    ("dialog_name_roi", "对话框名称区域"),
    ("claim_task_roi", "师门任务区域"),
    ("dialog_roi", "对话框区域"),
    ("confirm_give_roi", "确认赠送区域"),
    ("inventory_title_roi", "背包标题区域"),
]

def is_valid_relative_roi(roi: RelativeRegion | None) -> bool:
    """检查 RelativeRegion 是否为有效配置 (宽度和高度均大于 0)。"""
    if roi is None:
        return False
    return roi.width > 0.0 and roi.height > 0.0


async def main() -> None:
    print("🔍 正在查找系统中的梦幻西游游戏窗口...")
    rects = find_mhxy_window_rects(title_keyword="梦幻")

    if not rects:
        print("❌ 未找到运行中的梦幻西游游戏窗口！请确保游戏已被启动且窗口可见。")
        return

    sorted_rects = sort_window_rects(rects)
    target_win = sorted_rects[0]

    print(
        f"✅ 共找到 {len(sorted_rects)} 个游戏窗口。选择第 0 个窗口:\n"
        f"   - 句柄 (HWND): {target_win.hwnd}\n"
        f"   - 窗口分辨率: {target_win.width}x{target_win.height}"
    )

    # 1. 加载当前既有 MainHudLayoutConfig
    current_config = MainHudLayoutConfig()
    print("\n📋 检查既有 MainHudLayoutConfig 配置状态 (增量模式):")


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
        client = create_mhxy_client_by_index(index=0)
        async with client:
            print("\n📸 正在捕获游戏窗口画面...")
            await client.begin_frame()
            frame = await client.window.capture()

            total = len(need_calibrate)
            for idx, (field_name, desc) in enumerate(need_calibrate, start=1):
                print("\n" + "=" * 60)
                print(f"🖱️ 步骤 {idx}/{total}: 请框选 [{field_name}] ({desc})")
                print("   - 按 ENTER / SPACE 确认框选")
                print("   - 按 ESC 或 c 取消框选")
                print("=" * 60)

                window_title = f"[{idx}/{total}] Select {field_name} (Press ENTER/SPACE to confirm)"
                roi = await client.window.select_relative_roi(
                    window_name=window_title,
                    image=frame,
                )
                final_rois[field_name] = roi
    else:
        print("\n✨ 所有 ROI 字段均已在 config 中配置完成，无需额外标定！")

    # 3. 控制台格式化输出最新配置片段
    print("\n" + "=" * 70)
    print("🎉 标定/汇总完成！生成的 MainHudLayoutConfig 代码如下：")
    print("=" * 70)
    print("from dataclasses import dataclass")
    print("from client_core import RelativeRegion\n")
    print("@dataclass(frozen=True)")
    print("class MainHudLayoutConfig:")

    for field_name, desc in target_fields:
        val = final_rois.get(field_name)
        if is_valid_relative_roi(val):
            assert val is not None
            print(
                f"    {field_name}: RelativeRegion = RelativeRegion(x={val.x:.4f}, y={val.y:.4f}, width={val.width:.4f}, height={val.height:.4f})"
            )
        else:
            print(f"    # {field_name}: 未配置 ({desc})")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
