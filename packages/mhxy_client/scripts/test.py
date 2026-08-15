"""验证游戏鼠标匹配结果的独立脚本（基于预乘 Alpha 方案）。"""

from pathlib import Path
from typing import cast

import cv2
import numpy as np

def match_template_masked_patched(
    image: np.ndarray, template_rgba: np.ndarray
) -> tuple[float, tuple[int, int]]:
    """
    使用 OpenCV 原生 Mask 并带有防 NaN 预处理的模板匹配。
    """
    bgr = template_rgba[:, :, :3]
    alpha = template_rgba[:, :, 3]
    mask_3d = cv2.merge([alpha, alpha, alpha])

    # 1. 转换为 float32 以防计算过程中的上限溢出
    img_f32 = image.astype(np.float32)
    
    # 2. 【核心预处理】：消除截图矩阵中的绝对零值
    # 使用 np.maximum 将所有小于 1.0 的像素值强制提升为 1.0
    # 由于像素值域为 0-255，改变 1 个色阶对 TM_CCORR_NORMED 的最终得分影响在百万分之一以下
    img_f32 = np.maximum(img_f32, 1.0)

    bgr_f32 = bgr.astype(np.float32)
    mask_3d_f32 = mask_3d.astype(np.float32)

    # 3. 执行安全的带掩码匹配
    res = cv2.matchTemplate(
        img_f32, 
        bgr_f32, 
        cv2.TM_CCORR_NORMED, 
        mask=mask_3d_f32
    )

    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return float(max_val), cast(tuple[int, int], max_loc)

def match_template_robust(
    image: np.ndarray, template_rgba: np.ndarray
) -> tuple[float, tuple[int, int]]:
    """
    使用预乘 Alpha 方案进行高稳定性模板匹配。
    
    通过将模板透明区域的像素权值归零，避免调用 OpenCV 原生且存在缺陷的 mask 参数，
    从而安全地使用容错率最高的 TM_CCOEFF_NORMED 模式。
    """
    bgr = template_rgba[:, :, :3]
    alpha = template_rgba[:, :, 3]

    # 将 Alpha 通道归一化为 0.0 - 1.0 的浮点数权重
    alpha_weight = alpha.astype(np.float32) / 255.0
    mask_3d = cv2.merge([alpha_weight, alpha_weight, alpha_weight])

    # 预乘操作：保留主体像素，将透明背景变为纯黑色 (0, 0, 0)
    template_zeroed = (bgr * mask_3d).astype(np.uint8)

    # 避免降维丢失特征，直接使用 BGR 三通道矩阵进行匹配
    res = cv2.matchTemplate(image, template_zeroed, cv2.TM_CCOEFF_NORMED)

    # 获取最大相似度及其对应坐标
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return float(max_val), cast(tuple[int, int], max_loc)


def verify_game_mouse_match(
    screenshot_path: Path,
    cursor_template_path: Path,
    pointer_template_path: Path,
    threshold: float = 0.7,
) -> None:
    print("=" * 60)
    print(" 游戏鼠标模板匹配验证与诊断 (预乘 Alpha 方案) ")
    print("=" * 60)

    # 加载测试用例
    img = cv2.imread(str(screenshot_path))
    cursor_tpl = cv2.imread(str(cursor_template_path), cv2.IMREAD_UNCHANGED)
    pointer_tpl = cv2.imread(str(pointer_template_path), cv2.IMREAD_UNCHANGED)

    if img is None or cursor_tpl is None or pointer_tpl is None:
        print("Error: 无法读取图片或模板，请检查文件路径。")
        return

    # 执行匹配
    c_score, c_loc = match_template_masked_patched(img, cursor_tpl)
    p_score, p_loc = match_template_masked_patched(img, pointer_tpl)

    print(f"cursor.png  匹配得分: {c_score:.4f}, 位置 (top_left): {c_loc}")
    print(f"pointer.png 匹配得分: {p_score:.4f}, 位置 (top_left): {p_loc}")

    # 结果判定
    if c_score >= threshold or p_score >= threshold:
        if c_score > p_score:
            print(f"\n[成功] 成功匹配到普通光标 (cursor.png)！")
            print(f"匹配得分: {c_score:.4f} >= {threshold}")
            print(f"位置 top_left: {c_loc}")
        else:
            print(f"\n[成功] 成功匹配到点击指针 (pointer.png)！")
            print(f"匹配得分: {p_score:.4f} >= {threshold}")
            print(f"位置 top_left: {p_loc}")
    else:
        print(f"\n[失败] 两者匹配得分均未达到阈值 {threshold}")


if __name__ == "__main__":
    pkg_dir = Path(__file__).resolve().parents[1]
    verify_game_mouse_match(
        screenshot_path=pkg_dir / "screenshots" / "match_cursor_failed.png",
        cursor_template_path=pkg_dir / "templates" / "cursor.png",
        pointer_template_path=pkg_dir / "templates" / "pointer.png",
    )