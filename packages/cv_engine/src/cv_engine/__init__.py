"""cv_engine 门面层。

统一暴露对外 API、数据模型、异常、契约接口与 TemplateMatcher、OcrEngine 引擎。
"""

from cv_engine.backends import RapidOcrEngine
from cv_engine.constants import (
    DEFAULT_MATCH_THRESHOLD,
    DEFAULT_NMS_IOU_THRESHOLD,
    MatchMode,
)
from cv_engine.exceptions import (
    CVEngineError,
    InvalidImageError,
    MatchFailedError,
    OCRError,
    OcrFailedError,
    OcrInitError,
    TemplateNotFoundError,
)
from cv_engine.interfaces import IOCREngine, ITemplateMatcher
from cv_engine.models import MatLike, MatchResult, OcrResult, Point, Region
from cv_engine.ocr_engine import OcrEngine
from cv_engine.template_matcher import TemplateMatcher

__all__ = [
    # 统一接口契约
    "ITemplateMatcher",
    "IOCREngine",
    # 核心引擎实现
    "TemplateMatcher",
    "OcrEngine",
    "RapidOcrEngine",
    # 数据结构与类型
    "Point",
    "Region",
    "MatchResult",
    "OcrResult",
    "MatLike",
    # 常量与配置
    "MatchMode",
    "DEFAULT_MATCH_THRESHOLD",
    "DEFAULT_NMS_IOU_THRESHOLD",
    # 异常定义
    "CVEngineError",
    "TemplateNotFoundError",
    "InvalidImageError",
    "MatchFailedError",
    "OCRError",
    "OcrInitError",
    "OcrFailedError",
]
