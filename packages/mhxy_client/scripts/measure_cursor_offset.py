"""系统鼠标与游戏鼠标模板偏移量测试与点击校准脚本。

功能说明:
1. 首先获取梦幻西游游戏窗口，并将系统鼠标移至游戏窗口中心，以便观察原生鼠标与游戏鼠标的位置效果。
2. 读取系统物理鼠标当前绝对像素坐标 (GetCursorPos)，转换为窗口客户区相对坐标。
3. 在系统鼠标坐标周围 ±100px 范围 (200x200 像素 ROI) 内截取局部画面。
4. 使用指定的模板文件 (默认为 `templates/normal_cursor.png`，可通过 `--template` 参数指定) 进行模板匹配，定位游戏实际鼠标图像。
5. 提取匹配命中区域 (MatchResult.rect) 的【左上角 (rect.x, rect.y)】作为游戏鼠标的绝对物理点击原点。
6. 输出系统坐标、游戏鼠标左上角坐标以及两者之间的偏移向量 (Offset X/Y)。

使用说明:
   uv run python packages/mhxy_client/scripts/measure_cursor_offset.py [--template normal_cursor.png] [--threshold 0.7]
"""

import argparse
import asyncio
import logging
from pathlib import Path

from client_core import Point, Region, client_to_screen, get_cursor_pos
from mhxy_client import (
    create_mhxy_client_by_index,
    find_mhxy_window_rects,
    sort_window_rects,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="系统鼠标与游戏鼠标偏移量测试脚本"
    )
    parser.add_argument(
        "--template",
        type=str,
        default="cursor.png",
        help="模板文件名 (位于 templates/ 目录下，默认: cursor.png)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="模板匹配相似度阈值 (默认: 0.7)",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=50,
        help="以系统鼠标为中心搜索 ROI 的半径像素 (默认: 50，搜索 100x100 区域)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    raw_template: object = getattr(args, "template", "cursor.png")
    raw_threshold: object = getattr(args, "threshold", 0.7)
    raw_radius: object = getattr(args, "radius", 50)

    template_file = str(raw_template).strip()
    if not template_file.lower().endswith(".png"):
        template_file = f"{template_file}.png"

    threshold = float(str(raw_threshold))
    radius = int(str(raw_radius))

    # 确定模板文件路径: packages/mhxy_client/templates/<template_file>
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    template_path = templates_dir / template_file

    if not template_path.exists():
        print(f"❌ 模板文件不存在: {template_path}")
        print("💡 请先运行 capture_template.py 截取模板:")
        print(f"   uv run python packages/mhxy_client/scripts/capture_template.py --name {template_file}")
        return

    print("🔍 正在查找系统中的梦幻西游游戏窗口...")
    rects = find_mhxy_window_rects(title_keyword="梦幻")
    if not rects:
        print("❌ 未找到运行中的梦幻西游游戏窗口！请确保游戏已被启动且窗口可见。")
        return

    sorted_rects = sort_window_rects(rects)
    target_win = sorted_rects[0]
    print(
        f"✅ 找到游戏窗口 (HWND: {target_win.hwnd}, 分辨率: {target_win.width}x{target_win.height})"
    )

    client = create_mhxy_client_by_index(index=0)
    async with client:
        # 步骤 1: 第一次将鼠标移到窗口中心，观察效果
        center_client_x = target_win.width // 2
        center_client_y = target_win.height // 2
        center_point = Point(x=center_client_x, y=center_client_y)

        print(f"\n📍 第一次测试：移动系统鼠标至游戏窗口中心 ({center_client_x}, {center_client_y})...")
        await client.window.mouse_move(point=center_point)
        await asyncio.sleep(0.5)

        # 步骤 2: 读取当前系统鼠标的屏幕绝对坐标与窗口相对坐标
        sys_screen_pos = get_cursor_pos()
        # 将客户区 (0,0) 转换到屏幕，即可反算出系统鼠标在客户区的相对坐标
        client_origin_screen = client_to_screen(target_win.hwnd, Point(x=0, y=0))
        sys_client_x = sys_screen_pos.x - client_origin_screen.x
        sys_client_y = sys_screen_pos.y - client_origin_screen.y

        print(f"📊 当前系统鼠标绝对屏幕坐标: ({sys_screen_pos.x}, {sys_screen_pos.y})")
        print(f"📊 当前系统鼠标窗口客户区坐标: ({sys_client_x}, {sys_client_y})")

        # 步骤 3: 在系统鼠标周围 ±radius px 范围构建 ROI 区域
        roi_x = max(0, sys_client_x - radius)
        roi_y = max(0, sys_client_y - radius)
        roi_w = min(target_win.width - roi_x, radius * 2)
        roi_h = min(target_win.height - roi_y, radius * 2)
        search_roi = Region(x=roi_x, y=roi_y, width=roi_w, height=roi_h)

        print(f"\n🔎 正在鼠标附近 {search_roi.width}x{search_roi.height} 像素 ROI 内匹配游戏鼠标模板...")
        print(f"   - 检索区域 (ROI): {search_roi}")
        print(f"   - 模板路径: {template_path.resolve()}")
        print(f"   - 相似度阈值: {threshold}")

        match_res = await client.window.match_template(
            template=template_path,
            threshold=threshold,
            roi=search_roi,
        )

        if match_res is None:
            print("\n❌ 模板匹配失败！未在系统鼠标附近找到对应的游戏鼠标样式。")
            print("💡 建议:")
            print("   1. 检查游戏鼠标是否处于前台显示")
            print("   2. 尝试降低 --threshold 参数 (如 --threshold 0.5)")
            print("   3. 使用 capture_template.py 重新截取更精确的指针模板")
            return

        # 步骤 4: 匹配区域的左上角 (match_res.rect.x, match_res.rect.y) 作为游戏鼠标点击坐标
        game_mouse_top_left = Point(x=match_res.rect.x, y=match_res.rect.y)
        game_mouse_center = match_res.center

        # 计算偏移量 (游戏鼠标左上角 - 系统鼠标坐标)
        offset_x = game_mouse_top_left.x - sys_client_x
        offset_y = game_mouse_top_left.y - sys_client_y

        print("\n" + "=" * 70)
        print("🎯 匹配成功！游戏鼠标偏移统计结果：")
        print("=" * 70)
        print(f"   - 匹配相似度 Score : {match_res.score:.4f}")
        print(f"   - 系统鼠标客户区坐标: ({sys_client_x}, {sys_client_y})")
        print(f"   - 游戏鼠标左上角坐标: ({game_mouse_top_left.x}, {game_mouse_top_left.y}) [作为物理点击坐标]")
        print(f"   - 游戏鼠标中心匹配坐标: ({game_mouse_center.x}, {game_mouse_center.y})")
        print(f"   - 📐 相对偏移向量 (Offset): ΔX = {offset_x:+d} px,  ΔY = {offset_y:+d} px")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
