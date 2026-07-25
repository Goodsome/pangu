"""图像文字识别与定位引擎重定向与兼容模块。"""

from cv_engine.backends.base import BaseOcrEngine
from cv_engine.backends.rapid_ocr import RapidOcrEngine

# 默认使用支持 Python 3.14+ 的 RapidOcrEngine 作为 OcrEngine 通用别名
OcrEngine = RapidOcrEngine

__all__ = [
    "BaseOcrEngine",
    "RapidOcrEngine",
    "OcrEngine",
]
