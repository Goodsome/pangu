"""CV 引擎各个具体的后端实现模块包。"""

from cv_engine.backends.base import BaseOcrEngine
from cv_engine.backends.paddle_ocr import PaddleOcrEngine
from cv_engine.backends.rapid_ocr import RapidOcrEngine

__all__ = [
    "BaseOcrEngine",
    "PaddleOcrEngine",
    "RapidOcrEngine",
]
