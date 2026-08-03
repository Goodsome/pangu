"""截图捕获梦幻西游游戏 UI/鼠标/图标模板并保存至 templates 目录的脚本。

使用说明:
1. 确保梦幻西游游戏窗口开启且处于前台画面。
2. 执行脚本并传入 --name 参数:
   uv run python packages/mhxy_client/scripts/capture_template.py --name normal_cursor
3. 弹出 OpenCV GUI 框选窗口后，使用鼠标框选目标的图像区域。
4. 按 ENTER / SPACE 确认框选，模板图片将被自动裁剪并保存至 `packages/mhxy_client/templates/<name>.png`。
"""

import argparse
import asyncio
import logging
from pathlib import Path

import cv2
from mhxy_client import (
    create_mhxy_client_by_index,
    find_mhxy_window_rects,
    sort_window_rects,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="截取并保存梦幻西游游戏 UI/鼠标/图标模板"
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="模板保存文件名 (不需要含扩展名，如 '--name cursor_normal')",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    raw_name: object = getattr(args, "name", "")
    name_val = str(raw_name)
    template_name = name_val.strip()
    if not template_name:
        print("❌ 模板名称不能为空！")
        return

    # 确保扩展名正确处理
    if not template_name.lower().endswith(".png"):
        file_name = f"{template_name}.png"
    else:
        file_name = template_name

    # 确定保存路径: packages/mhxy_client/templates/<file_name>
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    save_path = templates_dir / file_name

    print("🔍 正在查找系统中的梦幻西游游戏窗口...")
    rects = find_mhxy_window_rects(title_keyword="梦幻")
    if not rects:
        print("❌ 未找到运行中的梦幻西游游戏窗口！请确保游戏已被启动且窗口可见。")
        return

    sorted_rects = sort_window_rects(rects)
    target_win = sorted_rects[0]
    print(
        f"✅ 找到 {len(sorted_rects)} 个窗口，选择第 0 个窗口 (HWND: {target_win.hwnd}, 分辨率: {target_win.width}x{target_win.height})"
    )

    client = create_mhxy_client_by_index(index=0)
    async with client:
        print("\n📸 正在捕获游戏窗口画面...")
        await client.begin_frame()
        frame = await client.window.capture()

        print("\n" + "=" * 60)
        print(f"🖱️ 请在弹出的窗口中框选模板区域 [保存名称: {file_name}]")
        print("   - 按 ENTER / SPACE 确认框选并保存")
        print("   - 按 ESC 或 c 取消框选")
        print("=" * 60)

        window_title = f"Select Template Region: {file_name} (Press ENTER/SPACE to confirm)"
        abs_region = await client.window.select_roi(
            window_name=window_title,
            image=frame,
        )

        if abs_region is None:
            print("⚠️ 已取消框选，未保存模板。")
            return

        # 裁剪并保存模板图像
        img_mat = frame.mat
        cropped = img_mat[
            abs_region.y : abs_region.y + abs_region.height,
            abs_region.x : abs_region.x + abs_region.width,
        ]

        cv2.imwrite(str(save_path), cropped)
        print("\n" + "=" * 60)
        print("🎉 模板保存成功！")
        print(f"   - 保存路径: {save_path.resolve()}")
        print(f"   - 选区坐标: x={abs_region.x}, y={abs_region.y}, width={abs_region.width}, height={abs_region.height}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
