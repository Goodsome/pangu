"""CV 引擎契约层。

定义模板匹配器 ITemplateMatcher 的 Protocol 接口规范。
"""

from pathlib import Path
from typing import Protocol, runtime_checkable

from cv_engine.constants import DEFAULT_MATCH_THRESHOLD, MatchMode
from cv_engine.models import MatLike, MatchResult, Region


@runtime_checkable
class ITemplateMatcher(Protocol):
    """通用模板匹配器接口契约。"""

    def load_template(self, template_path: Path | str) -> MatLike:
        """加载并缓存模板图片。"""
        ...

    def match_best(
        self,
        scene: MatLike | bytes,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
    ) -> MatchResult | None:
        """同步查找场景中单目标最佳匹配位置。"""
        ...

    def match_multi(
        self,
        scene: MatLike | bytes,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
        nms_threshold: float = 0.3,
    ) -> list[MatchResult]:
        """同步查找场景中所有符合阈值的多目标匹配列表（含 NMS 去重）。"""
        ...

    async def async_match_best(
        self,
        scene: MatLike | bytes,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
    ) -> MatchResult | None:
        """异步查找场景中单目标最佳匹配位置。"""
        ...

    async def async_match_multi(
        self,
        scene: MatLike | bytes,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
        nms_threshold: float = 0.3,
    ) -> list[MatchResult]:
        """异步查找场景中所有符合阈值的多目标匹配列表（含 NMS 去重）。"""
        ...

    def clear_cache(self) -> None:
        """清理已加载的模板缓存。"""
        ...
