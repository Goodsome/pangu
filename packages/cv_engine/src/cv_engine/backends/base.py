"""OCR 识别引擎通用基础基类。"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import override

import cv2
import numpy as np

from cv_engine.exceptions import InvalidImageError
from cv_engine.interfaces import IOCREngine
from cv_engine.models import MatLike, OcrResult, Region


@dataclass
class BaseOcrEngine(ABC, IOCREngine):
    """OCR 识别引擎通用基础基类，为具体的 OCR 后端提供通用的图像预处理与异步代理实现。"""

    @abstractmethod
    @override
    def ocr(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> list[OcrResult]:
        """同步识别场景中全部文本内容及其所在位置几何信息。"""
        ...

    @override
    def find_text(
        self,
        scene: MatLike,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
    ) -> OcrResult | None:
        """同步在场景图中检索特定的目标文本。"""
        all_items = self.ocr(scene, confidence_threshold=confidence_threshold, roi=roi)

        for item in all_items:
            if exact_match:
                if item.text == target_text:
                    return item
            else:
                if target_text in item.text:
                    return item

        return None

    @override
    async def async_ocr(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> list[OcrResult]:
        """异步识别场景中全部文本。"""
        return await asyncio.to_thread(self.ocr, scene, confidence_threshold, roi)

    @override
    async def async_find_text(
        self,
        scene: MatLike,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
    ) -> OcrResult | None:
        """异步在场景图中检索特定的目标文本。"""
        return await asyncio.to_thread(
            self.find_text, scene, target_text, confidence_threshold, exact_match, roi
        )

    # ---------------------------------------------------------------------------
    # 内部辅助方法
    # ---------------------------------------------------------------------------
    def _prepare_image_and_offset(
        self, scene: MatLike, roi: Region | None
    ) -> tuple[np.ndarray, int, int]:
        """将场景输入图像解析并规范化为 BGR 三通道矩阵，并计算 ROI 相对偏移量。"""
        if isinstance(scene, np.ndarray):
            if scene.size == 0:
                raise InvalidImageError("输入的图像矩阵 size 为 0")

            if scene.ndim == 2:
                img = cv2.cvtColor(scene, cv2.COLOR_GRAY2BGR)
            elif scene.ndim == 3:
                channels = int(scene.shape[2])
                if channels == 4:
                    img = cv2.cvtColor(scene, cv2.COLOR_BGRA2BGR)
                elif channels == 3:
                    img = scene
                elif channels == 1:
                    img = cv2.cvtColor(scene, cv2.COLOR_GRAY2BGR)
                else:
                    raise InvalidImageError(f"不支持的图像通道数: {channels}")
            else:
                raise InvalidImageError(f"不支持的图像维度: {scene.ndim}")
        else:
            raise InvalidImageError(f"不支持的场景图像格式类型: {type(scene)}")

        sh, sw = int(img.shape[0]), int(img.shape[1])
        offset_x, offset_y = 0, 0

        if roi is not None:
            x1 = max(0, min(roi.x, sw))
            y1 = max(0, min(roi.y, sh))
            x2 = max(0, min(roi.right, sw))
            y2 = max(0, min(roi.bottom, sh))

            if x2 <= x1 or y2 <= y1:
                raise InvalidImageError(f"请求的 ROI 检索切片区域无效: {roi}")

            img = img[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        return img, offset_x, offset_y
