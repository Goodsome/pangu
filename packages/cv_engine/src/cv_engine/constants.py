"""CV 引擎常量层。

定义模板匹配模式与默认阈值算法配置。
"""

from enum import Enum


class MatchMode(str, Enum):
    """OpenCV 模板匹配算法模式枚举。"""

    CCOEFF_NORMED = (
        "CCOEFF_NORMED"  # 标准化相关系数匹配 (最常用，结果介于 -1~1，推荐 0.8+)
    )
    CCORR_NORMED = "CCORR_NORMED"  # 标准化相关匹配 (结果介于 0~1)
    SQDIFF_NORMED = "SQDIFF_NORMED"  # 标准化平方差匹配 (0 表示完美匹配，越小越好)


DEFAULT_MATCH_THRESHOLD: float = 0.8
"""默认模板匹配概率阈值。"""

DEFAULT_NMS_IOU_THRESHOLD: float = 0.3
"""非极大值抑制 (NMS) 的重叠度 IoU 阈值。"""
