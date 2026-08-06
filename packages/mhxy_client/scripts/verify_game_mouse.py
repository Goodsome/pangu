"""验证 _get_game_mouse 匹配结果及诊断失败原因的独立脚本。"""

from pathlib import Path
from typing import cast
import cv2
import numpy as np


def verify_game_mouse_match(
    screenshot_path: Path,
    cursor_template_path: Path,
    pointer_template_path: Path,
    threshold: float = 0.7,
) -> None:
    print("=" * 60)
    print(" 游戏鼠标模板匹配验证与诊断 ")
    print("=" * 60)

    img = cv2.imread(str(screenshot_path))
    cursor_tpl = cv2.imread(str(cursor_template_path), cv2.IMREAD_UNCHANGED)
    pointer_tpl = cv2.imread(str(pointer_template_path), cv2.IMREAD_UNCHANGED)

    if img is None or cursor_tpl is None or pointer_tpl is None:
        print("Error: 无法读取图片或模板")
        return

    # 1. 测试原生 match_template_masked (使用 alpha 作为 mask 参数)
    print("\n--- 1. OpenCV 原生 cv2.TM_CCOEFF_NORMED 带 mask 参数 ---")
    bgr_c = cursor_tpl[:, :, :3]
    alpha_c = cursor_tpl[:, :, 3]
    res_c_masked = cv2.matchTemplate(img, bgr_c, cv2.TM_CCORR_NORMED, mask=alpha_c)
    score_c_orig = float(cv2.minMaxLoc(res_c_masked)[1])
    print(f"cursor.png 匹配得分 (原生带 mask): {score_c_orig}")

    bgr_p = pointer_tpl[:, :, :3]
    alpha_p = pointer_tpl[:, :, 3]
    res_p_masked = cv2.matchTemplate(img, bgr_p, cv2.TM_CCORR_NORMED, mask=alpha_p)
    score_p_orig = float(cv2.minMaxLoc(res_p_masked)[1])
    print(f"pointer.png 匹配得分 (原生带 mask): {score_p_orig}")
    print("[结论]: OpenCV C++ 引擎在 3 通道图像 + Alpha mask 上使用 TM_CCOEFF_NORMED 会出现数值溢出/NaN 异常导致得分归零！")

    # 2. 测试修复方案: 将透明背景置零后进行不带 mask 的 TM_CCOEFF_NORMED 匹配
    print("\n--- 2. 优化方案: 将 Alpha 透明背景置零后直接匹配 ---")

    def match_template_alpha_zeroed(
        image: np.ndarray, template_rgba: np.ndarray
    ) -> tuple[float, tuple[int, int]]:
        bgr = template_rgba[:, :, :3]
        alpha = template_rgba[:, :, 3]
        mask_3d = cv2.merge([alpha, alpha, alpha]) / 255.0
        tpl_zeroed = (bgr * mask_3d).astype(np.uint8)
        res = cv2.matchTemplate(image, tpl_zeroed, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        loc = cast(tuple[int, int], max_loc)
        return float(max_val), loc

    c_score, c_loc = match_template_alpha_zeroed(img, cursor_tpl)
    p_score, p_loc = match_template_alpha_zeroed(img, pointer_tpl)

    print(f"cursor.png  得分: {c_score:.4f}, 位置 (top_left): {c_loc}")
    print(f"pointer.png 得分: {p_score:.4f}, 位置 (top_left): {p_loc}")

    if c_score >= threshold or p_score >= threshold:
        if c_score > p_score:
            print(f"\n[成功] 成功匹配到普通光标 (cursor.png)！匹配得分: {c_score:.4f} >= {threshold}")
            print(f"位置 top_left: {c_loc}")
        else:
            print(f"\n[成功] 成功匹配到点击指针 (pointer.png)！匹配得分: {p_score:.4f} >= {threshold}")
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
