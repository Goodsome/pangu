import cv2
from cv_engine.models import MatLike

def _normalize_scene_bgr(scene: MatLike) -> MatLike:
    """
    将场景输入图像规范化解析为 3D BGR 三通道矩阵。
    """
    if scene.size == 0:
        raise ValueError("场景图像矩阵 size 为 0")

    if scene.ndim == 2:
        return cv2.cvtColor(scene, cv2.COLOR_GRAY2BGR)
    if scene.ndim == 3:
        channels = int(scene.shape[2])
        if channels == 4:
            return cv2.cvtColor(scene, cv2.COLOR_BGRA2BGR)
        if channels == 3:
            return scene

    raise ValueError("不支持的场景图像格式类型")

def abs_diff(
    img1: MatLike, 
    img2: MatLike, 
    pixel_threshold: int = 30, 
    diff_ratio_threshold: float = 0.01
) -> bool:
    """
    使用绝对差分检查区域是否发生变化。
    
    Args:
        img1: 图像基准区域矩阵
        img2: 图像当前区域矩阵
        pixel_threshold: 单个像素容差阈值 (0-255，抵抗极微小的渲染波动)
        diff_ratio_threshold: 允许发生变化的像素总面积比例 (例如 0.01 代表 1%)
        
    Returns:
        bool: 是否发生了明显变化
    """
    img1 = _normalize_scene_bgr(img1)
    img2 = _normalize_scene_bgr(img2)
    
    if img1.shape != img2.shape:
        raise ValueError("对比区域的尺寸或通道数不一致")

    # 1. 计算绝对差值矩阵
    diff = cv2.absdiff(img1, img2)

    # 2. 降维至单通道便于统计
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) if diff.ndim == 3 else diff

    # 3. 过滤掉低于容差的微小波动，将明显差异二值化
    _, thresh = cv2.threshold(diff_gray, pixel_threshold, 255, cv2.THRESH_BINARY)

    # 4. 统计发生变化的像素比例
    changed_pixels = cv2.countNonZero(thresh)
    total_pixels = diff_gray.size
    ratio = changed_pixels / total_pixels

    return ratio > diff_ratio_threshold