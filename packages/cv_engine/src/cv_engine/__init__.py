"""cv_engine 门面层。

统一暴露对外 API、数据模型、异常、契约接口与 TemplateMatcher 匹配引擎。
"""

from cv_engine.constants import (
    DEFAULT_MATCH_THRESHOLD,
    DEFAULT_NMS_IOU_THRESHOLD,
    MatchMode,
)
from cv_engine.exceptions import (
    CVEngineError,
    InvalidImageError,
    MatchFailedError,
    TemplateNotFoundError,
)
from cv_engine.interfaces import ITemplateMatcher
from cv_engine.models import MatLike, MatchResult, Point, Region
from cv_engine.template_matcher import TemplateMatcher

__all__ = [
    # 统一接口契约
    "ITemplateMatcher",
    # 核心引擎实现
    "TemplateMatcher",
    # 数据结构与类型
    "Point",
    "Region",
    "MatchResult",
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
]
