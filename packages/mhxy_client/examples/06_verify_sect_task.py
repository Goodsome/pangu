# -*- coding: utf-8 -*-
"""示例 6: 检查并慢移/点击领取 MainHUD 师门任务 (06_verify_sect_task.py)。

说明：
    基于 foundation.configure_logging 配置全局日志保存至 logs/mhxy_client.log，
    自动获取运行中的梦幻西游游戏窗口，
    通过 client.main_hud 访问 MainHUD 页面对象，
    调用 await hud.check_sect_task() 解析师门任务状态，
    若判定为 CLAIMABLE，调用 await hud.claim_sect_task(smooth_move=True, smooth_duration_sec=1.0, delay_before_click_sec=1.0)
    实现鼠标指针 1.0 秒超平滑缓慢划过去，并生成包含红色打靶准星的可视化调试截图 screenshots/sect_task_target_point.png。

运行方式：
    uv run python packages/mhxy_client/examples/06_verify_sect_task.py
"""

import asyncio
import ctypes
import logging
import sys
from pathlib import Path

import cv2

pkg_src = Path(__file__).resolve().parent.parent / "src"
if str(pkg_src) not in sys.path:
    sys.path.insert(0, str(pkg_src))

from foundation import configure_logging  # noqa: E402
from mhxy_client import (  # noqa: E402
    SectTaskStatus,
    create_mhxy_client_by_index,
    find_mhxy_window_rects,
)

# ==============================================================================
# 🎛️ 调试控制选项:
#  - MOVE_ONLY           : True 仅缓慢划至 '师父' 文字，不点击 (用于目测光标校准)
#  - SMOOTH_MOVE         : True 开启仿真平滑缓慢划动，避免物理光标瞬移产生的惯性下漂
#  - SMOOTH_DURATION_SEC : 慢速移动插值耗时 (秒，默认 1.0s)
#  - DELAY_SEC           : 停靠后悬停沉淀等待的时间 (秒，默认 1.0s)
# ==============================================================================
MOVE_ONLY: bool = False
SMOOTH_MOVE: bool = True
SMOOTH_DURATION_SEC: float = 1.0
DELAY_BEFORE_CLICK_SEC: float = 1.0

# 开启物理 1:1 High-DPI 感知
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

# 使用 foundation 日志配置，统一输出并持久化保存至 logs/mhxy_client.log
log_dir = Path(__file__).resolve().parent.parent.parent.parent / "logs"
configure_logging(app_name="mhxy_client", log_dir=log_dir, log_level=logging.INFO)
logger = logging.getLogger("mhxy_client.check_sect_task")


async def async_main() -> None:
    logger.info("=" * 75)
    logger.info(
        "  [MHXY Client] 示例 6: MainHUD 师门任务 (Sect Task) 慢速移动与实测坐标打靶追踪"
    )
    logger.info("=" * 75)
    logger.info(
        f"  * 运行模式设置 : MOVE_ONLY={MOVE_ONLY}, SMOOTH_MOVE={SMOOTH_MOVE}, 慢移耗时={SMOOTH_DURATION_SEC}s, 沉淀等待={DELAY_BEFORE_CLICK_SEC}s"
    )

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
        hud = client.main_hud
        hud.window.activate()

        # 1. 抓取并保存 task_list_roi 调试切片图
        roi = hud.config.task_list_roi
        roi_save_path = Path("screenshots/sect_task_debug_roi.png").resolve()
        roi_save_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"\n[Vision] 正在捕获任务列表区域画面 (ROI: {roi})...")
        frame = await client.window.capture(region=roi)
        if frame.mat is not None:
            await frame.save(roi_save_path)
            logger.info(f"📷 任务列表 ROI 截图已保存至: {roi_save_path.as_uri()}")

        # 2. 执行 MainHUD.check_sect_task 并打印状态汇总
        logger.info("\n[HUD] 正在调用 client.main_hud.check_sect_task()...")
        task_info = await hud.check_sect_task()

        logger.info("\n🎉 师门任务解析结果汇总:")
        print("=" * 75)
        print(f"  * 任务追踪面板开启 : {task_info.is_tracking_panel_open}")
        print(f"  * 师门任务处于追踪 : {task_info.is_sect_task_active}")
        print(
            f"  * 师门任务当前状态 : {task_info.status.value} (enum: {task_info.status})"
        )
        print(f"  * 描述多行文本     : {task_info.description_lines}")
        print(f"  * 匹配目标交互文本 : '{task_info.action_text}'")
        print(f"  * 交互点击窗口坐标 : {task_info.action_point}")
        print("=" * 75)

        # 2.5 绘制打靶红十字准星图
        if frame.mat is not None and task_info.action_point is not None:
            annotated_mat = frame.mat.copy()
            abs_roi = client.window._resolve_region(roi)
            if abs_roi is not None:
                roi_pt_x = task_info.action_point.x - abs_roi.x
                roi_pt_y = task_info.action_point.y - abs_roi.y

                # 绘制鲜红色的十字靶心 (BGR: 0, 0, 255)
                cv2.drawMarker(
                    annotated_mat,
                    (roi_pt_x, roi_pt_y),
                    color=(0, 0, 255),
                    markerType=cv2.MARKER_CROSS,
                    markerSize=16,
                    thickness=2,
                )
                cv2.circle(annotated_mat, (roi_pt_x, roi_pt_y), 6, (0, 0, 255), 1)

                target_img_path = Path(
                    "screenshots/sect_task_target_point.png"
                ).resolve()
                cv2.imwrite(str(target_img_path), annotated_mat)
                logger.info(
                    f"🎯 [打靶可视化] 已在 ROI 截图中绘制算得的目标坐标十字准星: {target_img_path.as_uri()}"
                )


    logger.info("=" * 75)
    logger.info(
        f"📄 完整的日志已成功保存写入至文件: {(log_dir / 'mhxy_client.log').resolve()}"
    )


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
