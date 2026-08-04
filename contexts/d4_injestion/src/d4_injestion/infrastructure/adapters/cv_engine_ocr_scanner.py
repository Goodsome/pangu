"""基于 cv_engine.RapidOcrEngine 的 OCR 识别适配器。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import override

from cv_engine import RapidOcrEngine
from cv_engine.models import MatLike, OcrResult

from d4_injestion.application.ports.ocr_scanner import OcrScanner
from d4_injestion.domain.value_objects.ocr_text_block import OcrTextBlock


@dataclass
class CvEngineOcrScanner(OcrScanner):
    """使用 cv_engine RapidOcrEngine 识别图像矩阵的适配器。"""

    engine: RapidOcrEngine = field(default_factory=RapidOcrEngine)

    @override
    def scan(
        self,
        image: MatLike,
        confidence_threshold: float = 0.5,
    ) -> list[OcrTextBlock]:
        """识别图像矩阵中的全部文本并映射为领域 OCR 文本块。"""
        ...

    def _to_block(self, result: OcrResult) -> OcrTextBlock:
        """将 cv_engine.OcrResult 映射为领域 OcrTextBlock。"""
        ...
