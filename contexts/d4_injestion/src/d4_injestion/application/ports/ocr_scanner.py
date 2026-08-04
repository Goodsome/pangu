"""OCR 识别端口：对图像矩阵做文字识别，返回领域 OCR 文本块。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from cv_engine.models import MatLike

from d4_injestion.domain.value_objects.ocr_text_block import OcrTextBlock


class OcrScanner(ABC):
    """图像矩阵 -> OCR 文本块识别器端口。"""

    @abstractmethod
    def scan(
        self,
        image: MatLike,
        confidence_threshold: float = 0.5,
    ) -> list[OcrTextBlock]:
        """识别图像矩阵中的全部文本。

        Args:
            image: BGR 三通道 ndarray 图像矩阵。
            confidence_threshold: 置信度过滤阈值。
        """
        ...
