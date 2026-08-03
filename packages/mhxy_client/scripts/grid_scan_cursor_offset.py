"""全窗口网格采样与游戏鼠标偏移规律分析脚本 (Grid Scan Cursor Offset)。

支持控制变量法测试:
- --radius: 搜索 ROI 半径 (默认 150px，覆盖 300x300 范围，解决大偏移漏捕获)
- --delay: 移动后沉淀等待时间 (默认 0.5s，解决鼠标渲染延迟)
- --smooth: 是否开启平滑移动 (默认开启)
- --cols / --rows: 网格密度
- 文件名包含时间戳，多次执行记录不被覆盖
"""

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import math
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


@dataclass
class SamplePoint:
    grid_col: int
    grid_row: int
    sys_client_x: int
    sys_client_y: int
    sys_screen_x: int
    sys_screen_y: int
    game_top_left_x: int
    game_top_left_y: int
    game_center_x: int
    game_center_y: int
    delta_x: int
    delta_y: int
    pred_game_top_left_x: int
    pred_game_top_left_y: int
    pred_error_x_px: int
    pred_error_y_px: int
    pred_error_dist_px: float
    pred_error_rate_pct: float
    match_score: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="全窗口网格采样与游戏鼠标偏移规律分析脚本"
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
        default=0.6,
        help="模板匹配相似度阈值 (默认: 0.6)",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=50,
        help="以系统鼠标为中心搜索 ROI 的半径像素 (默认: 50，即 100x100 区域)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="鼠标移动到位后的等待沉淀时间秒数 (默认: 0.5s)",
    )
    parser.add_argument(
        "--smooth",
        action="store_true",
        default=True,
        help="使用平滑移动 (默认开启)",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=5,
        help="水平采样网格列数 (默认: 5)",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=5,
        help="垂直采样网格行数 (默认: 5)",
    )
    parser.add_argument(
        "--margin-ratio",
        type=float,
        default=0.1,
        help="窗口边缘安全留白比例 (0.0~0.4，默认 0.1 即避开极度靠边处)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    raw_template: object = getattr(args, "template", "cursor.png")
    raw_threshold: object = getattr(args, "threshold", 0.6)
    raw_radius: object = getattr(args, "radius", 150)
    raw_delay: object = getattr(args, "delay", 0.5)
    raw_smooth: object = getattr(args, "smooth", True)
    raw_cols: object = getattr(args, "cols", 5)
    raw_rows: object = getattr(args, "rows", 5)
    raw_margin: object = getattr(args, "margin_ratio", 0.1)

    template_file = str(raw_template).strip()
    if not template_file.lower().endswith(".png"):
        template_file = f"{template_file}.png"

    threshold = float(str(raw_threshold))
    radius = int(str(raw_radius))
    delay_sec = float(str(raw_delay))
    smooth_move = bool(raw_smooth)
    cols = max(2, int(str(raw_cols)))
    rows = max(2, int(str(raw_rows)))
    margin_ratio = float(str(raw_margin))

    # 确定模板文件路径: packages/mhxy_client/templates/<template_file>
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    template_path = templates_dir / template_file

    if not template_path.exists():
        print(f"❌ 模板文件不存在: {template_path}")
        print("💡 请先运行 capture_template.py 截取模板:")
        print(
            f"   uv run python packages/mhxy_client/scripts/capture_template.py --name {template_file}"
        )
        return

    print("🔍 正在查找系统中的梦幻西游游戏窗口...")
    rects = find_mhxy_window_rects(title_keyword="梦幻")
    if not rects:
        print("❌ 未找到运行中的梦幻西游游戏窗口！请确保游戏已被启动且窗口可见。")
        return

    sorted_rects = sort_window_rects(rects)
    target_win = sorted_rects[0]
    win_w = target_win.width
    win_h = target_win.height

    print(
        f"✅ 找到游戏窗口 (HWND: {target_win.hwnd}, 分辨率: {win_w}x{win_h})"
    )
    print(f"🎯 控制变量参数:")
    print(f"   - 网格: {cols}x{rows} (共 {cols * rows} 点)")
    print(f"   - ROI 半径: {radius} px (搜索区域 {radius*2}x{radius*2})")
    print(f"   - 沉淀延时: {delay_sec} s | 平滑移动: {smooth_move} | 阈值: {threshold}")

    # 计算网格坐标序列
    margin_x = int(win_w * margin_ratio)
    margin_y = int(win_h * margin_ratio)
    usable_w = win_w - 2 * margin_x
    usable_h = win_h - 2 * margin_y

    x_step = usable_w / (cols - 1) if cols > 1 else 0
    y_step = usable_h / (rows - 1) if rows > 1 else 0

    grid_targets: list[tuple[int, int, int, int]] = []
    for r in range(rows):
        for c in range(cols):
            cx = int(margin_x + c * x_step)
            cy = int(margin_y + r * y_step)
            grid_targets.append((c, r, cx, cy))

    samples: list[SamplePoint] = []
    client = create_mhxy_client_by_index(index=0)

    # 每次整体脚本运行只创建一个以 run_时间戳 命名的独立调试文件夹
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_dir = Path(__file__).resolve().parent.parent / "output" / "debug_matches" / f"run_{run_timestamp}"
    debug_dir.mkdir(parents=True, exist_ok=True)

    async with client:
        print("\n🚀 开始执行网格自动化采样测定...")
        print(f"📁 调试截图将保存至单文件夹: {debug_dir.resolve()}")
        total = len(grid_targets)

        for idx, (c, r, target_x, target_y) in enumerate(grid_targets, start=1):
            print(
                f"\r⏳ [进度 {idx}/{total}] 正在移动至网格 ({c},{r}) -> 客户区目标 ({target_x}, {target_y})...",
                end="",
                flush=True,
            )

            target_pt = Point(x=target_x, y=target_y)
            # 1. 移动系统鼠标到测试目标点
            if smooth_move:
                await client.window.smooth_mouse_move(point=target_pt, steps=15, duration_sec=0.2)
            else:
                await client.window.mouse_move(point=target_pt)

            if delay_sec > 0:
                await asyncio.sleep(delay_sec)  # 沉淀等待渲染稳定

            # 2. 获取实际鼠标位置
            sys_screen_pos = get_cursor_pos()
            client_origin_screen = client_to_screen(target_win.hwnd, Point(x=0, y=0))
            sys_client_x = sys_screen_pos.x - client_origin_screen.x
            sys_client_y = sys_screen_pos.y - client_origin_screen.y

            # 3. 构造 ROI (使用配置的 radius，防止越界)
            roi_x = max(0, sys_client_x - radius)
            roi_y = max(0, sys_client_y - radius)
            roi_w = min(win_w - roi_x, radius * 2)
            roi_h = min(win_h - roi_y, radius * 2)
            search_roi = Region(x=roi_x, y=roi_y, width=roi_w, height=roi_h)

            # 4. 显式触发 begin_frame() 刷新单帧画面缓存，确保获取最新的物理渲染画面
            await client.begin_frame()
            frame = await client.window.capture()
            img_mat = frame.mat.copy()

            # 4. 匹配模板
            match_res = await client.window.match_template(
                template=template_path,
                threshold=threshold,
                roi=search_roi,
            )

            # 在图像上绘制调试标注 (无论匹配是否成功)
            import cv2

            # 绘制系统鼠标请求的目标中心 (红点与十字准星)
            cv2.circle(img_mat, (sys_client_x, sys_client_y), 5, (0, 0, 255), -1)  # 红点
            cv2.drawMarker(img_mat, (sys_client_x, sys_client_y), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)

            # 绘制 300x300 ROI 搜索框 (黄色细框)
            cv2.rectangle(
                img_mat,
                (search_roi.x, search_roi.y),
                (search_roi.x + search_roi.width, search_roi.y + search_roi.height),
                (0, 255, 255),
                1,
            )

            if match_res is not None:
                game_top_left_x = match_res.rect.x
                game_top_left_y = match_res.rect.y
                delta_x = game_top_left_x - sys_client_x
                delta_y = game_top_left_y - sys_client_y

                # 基于线性拉伸数学模型计算预测的游戏鼠标左上角坐标:
                # ΔY = 0.024 * (Y_sys - 511) - 1.0
                # ΔX = 0.045 * (X_sys - 646) + 18.5
                pred_delta_y = 0.024 * (sys_client_y - 511.0) - 1.0
                pred_delta_x = 0.045 * (sys_client_x - 646.0) + 18.5
                pred_game_top_left_x = int(round(sys_client_x + pred_delta_x))
                pred_game_top_left_y = int(round(sys_client_y + pred_delta_y))

                # 计算预测误差 (像素与百分比)
                err_x_px = pred_game_top_left_x - game_top_left_x
                err_y_px = pred_game_top_left_y - game_top_left_y
                err_dist_px = math.sqrt(err_x_px**2 + err_y_px**2)

                # 相对坐标距离基准的预测误差率 (%)
                diagonal_len = math.sqrt(win_w**2 + win_h**2)
                err_rate_pct = (err_dist_px / diagonal_len) * 100.0 if diagonal_len > 0 else 0.0

                # 绘制预测出的点 (蓝色小圆圈与十字圈)
                cv2.circle(img_mat, (pred_game_top_left_x, pred_game_top_left_y), 4, (255, 0, 0), -1)
                cv2.drawMarker(img_mat, (pred_game_top_left_x, pred_game_top_left_y), (255, 0, 0), cv2.MARKER_TILTED_CROSS, 12, 1)

                # 绘制匹配命中的游戏鼠标矩形框 (绿色实线)
                cv2.rectangle(
                    img_mat,
                    (match_res.rect.x, match_res.rect.y),
                    (match_res.rect.x + match_res.rect.width, match_res.rect.y + match_res.rect.height),
                    (0, 255, 0),
                    2,
                )
                # 在左上角标注匹配得分、预测坐标与绝对误差
                label = f"Score:{match_res.score:.2f} (dx:{delta_x}, dy:{delta_y}) Err:{err_dist_px:.1f}px"
                cv2.putText(
                    img_mat,
                    label,
                    (match_res.rect.x, max(15, match_res.rect.y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

                sp = SamplePoint(
                    grid_col=c,
                    grid_row=r,
                    sys_client_x=sys_client_x,
                    sys_client_y=sys_client_y,
                    sys_screen_x=sys_screen_pos.x,
                    sys_screen_y=sys_screen_pos.y,
                    game_top_left_x=game_top_left_x,
                    game_top_left_y=game_top_left_y,
                    game_center_x=match_res.center.x,
                    game_center_y=match_res.center.y,
                    delta_x=delta_x,
                    delta_y=delta_y,
                    pred_game_top_left_x=pred_game_top_left_x,
                    pred_game_top_left_y=pred_game_top_left_y,
                    pred_error_x_px=err_x_px,
                    pred_error_y_px=err_y_px,
                    pred_error_dist_px=round(err_dist_px, 2),
                    pred_error_rate_pct=round(err_rate_pct, 4),
                    match_score=float(match_res.score),
                )
                samples.append(sp)

            # 保存调试图片到当次运行的同一个文件夹中
            status_tag = f"score_{match_res.score:.2f}" if match_res else "FAILED"
            img_name = f"grid_{c}_{r}_sys({sys_client_x},{sys_client_y})_{status_tag}.png"
            cv2.imwrite(str(debug_dir / img_name), img_mat)

        print("\n✅ 网格采样完毕！\n")

    if not samples:
        print("❌ 未采到任何有效的样本，请检查模板和匹配阈值。")
        return

    # 数据统计与分析
    delta_xs = [s.delta_x for s in samples]
    delta_ys = [s.delta_y for s in samples]

    avg_dx = sum(delta_xs) / len(delta_xs)
    avg_dy = sum(delta_ys) / len(delta_ys)

    min_dx, max_dx = min(delta_xs), max(delta_xs)
    min_dy, max_dy = min(delta_ys), max(delta_ys)

    var_dx = sum((x - avg_dx) ** 2 for x in delta_xs) / len(delta_xs)
    var_dy = sum((y - avg_dy) ** 2 for y in delta_ys) / len(delta_ys)
    std_dx = math.sqrt(var_dx)
    std_dy = math.sqrt(var_dy)

    err_dists = [s.pred_error_dist_px for s in samples]
    err_rates = [s.pred_error_rate_pct for s in samples]
    avg_err_dist = sum(err_dists) / len(err_dists)
    avg_err_rate = sum(err_rates) / len(err_rates)

    print("=" * 85)
    print(f"📊 采样分析与模型预测校验总结 (有效样本数: {len(samples)}/{len(grid_targets)})")
    print("=" * 85)
    print(
        f"  • ΔX (游戏鼠标左上角 - 系统鼠标X): 平均 = {avg_dx:+.2f} px | 标准差 = {std_dx:.2f} | 范围 = [{min_dx:+d}, {max_dx:+d}]"
    )
    print(
        f"  • ΔY (游戏鼠标左上角 - 系统鼠标Y): 平均 = {avg_dy:+.2f} px | 标准差 = {std_dy:.2f} | 范围 = [{min_dy:+d}, {max_dy:+d}]"
    )
    print(
        f"  • 📐 线性回归模型预测误差: 平均距离误差 = {avg_err_dist:.2f} px | 平均相对误差率 = {avg_err_rate:.4f}%"
    )
    print("-" * 85)

    print("-" * 85)
    print("网格位置(c,r) | 系统坐标 (X,Y) | 实际游戏鼠标(X,Y) | 线性预测(X,Y) | 距离误差(px) | 误差率(%) | 匹配度")
    print("-" * 85)
    for s in samples:
        print(
            f"  ({s.grid_col},{s.grid_row})     | ({s.sys_client_x:4d}, {s.sys_client_y:4d}) | ({s.game_top_left_x:4d}, {s.game_top_left_y:4d})  | ({s.pred_game_top_left_x:4d}, {s.pred_game_top_left_y:4d})  | {s.pred_error_dist_px:7.2f} px | {s.pred_error_rate_pct:7.4f}% | {s.match_score:.3f}"
        )
    print("=" * 85 + "\n")

    # 带时间戳导出 JSON，防止历史记录被覆盖
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"samples_{cols}x{rows}_r{radius}_d{delay_sec}_{timestamp_str}.json"

    export_data = {
        "timestamp": timestamp_str,
        "config": {
            "template": template_file,
            "threshold": threshold,
            "radius": radius,
            "delay_sec": delay_sec,
            "smooth_move": smooth_move,
            "cols": cols,
            "rows": rows,
        },
        "window": {"width": win_w, "height": win_h},
        "statistics": {
            "valid_samples": len(samples),
            "avg_delta_x": avg_dx,
            "avg_delta_y": avg_dy,
            "std_delta_x": std_dx,
            "std_delta_y": std_dy,
            "min_delta_x": min_dx,
            "max_delta_x": max_dx,
            "min_delta_y": min_dy,
            "max_delta_y": max_dy,
        },
        "samples": [asdict(s) for s in samples],
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"📁 详细采样 JSON 数据已导出保存至: {json_path.resolve()}\n")


if __name__ == "__main__":
    asyncio.run(main())
