"""CV 引擎契约层。

定义模板匹配器 ITemplateMatcher 与 OCR 引擎 IOCREngine 的 Protocol 接口规范。
"""

from pathlib import Path
from typing import Protocol, runtime_checkable

from cv_engine.constants import DEFAULT_MATCH_THRESHOLD, MatchMode
from cv_engine.models import MatLike, MatchResult, OcrResult, Region


@runtime_checkable
class ITemplateMatcher(Protocol):
    """通用模板匹配器接口契约。"""

    def load_template(self, template_path: Path | str) -> MatLike:
        """加载并缓存模板图片。"""
        ...

    def match_best(
        self,
        scene: MatLike,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
    ) -> MatchResult | None:
        """同步查找场景中单目标最佳匹配位置。"""
        ...

    def match_multi(
        self,
        scene: MatLike,
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
        scene: MatLike,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
    ) -> MatchResult | None:
        """异步查找场景中单目标最佳匹配位置。"""
        ...

    async def async_match_multi(
        self,
        scene: MatLike,
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

    def match_masked_template(
        self,
        scene: MatLike,
        template: Path,
        roi: Region | None = None,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
    ) -> MatchResult | None:
        ...

@runtime_checkable
class IOCREngine(Protocol):
    """通用 OCR 识别引擎接口契约。"""

    def ocr(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> list[OcrResult]:
        """同步识别场景中全部文本内容及其所在位置几何信息。"""
        ...

    def find_text(
        self,
        scene: MatLike,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
    ) -> OcrResult | None:
        """同步在场景图中检索特定的目标文本。"""
        ...

    async def async_ocr(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> list[OcrResult]:
        """异步识别场景中全部文本。"""
        ...

    async def async_find_text(
        self,
        scene: MatLike,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
    ) -> OcrResult | None:
        """异步在场景图中检索特定的目标文本。"""
        ...
