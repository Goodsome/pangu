"""基于 PaddleOCR 的图像文字识别与定位引擎实现。"""

import asyncio
from dataclasses import dataclass, field
import logging
from typing import Any, override

import cv2
import numpy as np

from cv_engine.exceptions import InvalidImageError, OcrFailedError, OcrInitError
from cv_engine.interfaces import IOCREngine
from cv_engine.models import MatLike, OcrResult, Point, Region

logger = logging.getLogger(__name__)


@dataclass
class OcrEngine(IOCREngine):
    """基于 PaddleOCR 的文字识别与空间定位引擎。

    提供从图像或二进制字节流中识别中文/英文文本及精准定位位置外接矩形与中心坐标的能力。
    """

    lang: str = "ch"
    use_gpu: bool = False
    use_angle_cls: bool = True
    show_log: bool = False

    # 外部注入或懒加载的 paddleocr.PaddleOCR 实例
    ocr_instance: Any = field(default=None, repr=False)
    _ocr_app: Any = field(default=None, repr=False)

    def _get_ocr_app(self) -> Any:
        """获取或延迟初始化 PaddleOCR 识别实例。"""
        if self.ocr_instance is not None:
            return self.ocr_instance

        if self._ocr_app is not None:
            return self._ocr_app

        try:
            from paddleocr import PaddleOCR
        except ImportError as e:
            raise OcrInitError(
                "未找到 paddleocr 依赖包，请先安装: pip install paddleocr paddlepaddle"
            ) from e

        try:
            # 优先构建符合最新版 PaddleOCR 规范的参数字典 (移除了已被废弃的 use_gpu 和 show_log)
            init_kwargs: dict[str, Any] = {"lang": self.lang}

            # 设备设置：新版使用 device 参数 (如 'cpu' 或 'gpu')，避免传 use_gpu 导致 ValueError: Unknown argument
            init_kwargs["device"] = "gpu" if self.use_gpu else "cpu"

            # 方向文本识别：新版推荐使用 use_textline_orientation 替代 use_angle_cls
            init_kwargs["use_textline_orientation"] = self.use_angle_cls

            try:
                self._ocr_app = PaddleOCR(**init_kwargs)
            except (ValueError, TypeError):
                # 兼容旧版本 PaddleOCR 入参签名
                fallback_kwargs: dict[str, Any] = {
                    "lang": self.lang,
                    "use_angle_cls": self.use_angle_cls,
                }
                if self.use_gpu:
                    fallback_kwargs["use_gpu"] = True
                self._ocr_app = PaddleOCR(**fallback_kwargs)

            return self._ocr_app
        except Exception as e:
            raise OcrInitError(f"初始化 PaddleOCR 引擎失败: {e}") from e

    @override
    def ocr(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> list[OcrResult]:
        """同步识别场景中全部文本内容及其所在位置几何信息。

        Args:
            scene: 输入图像 (支持 NumPy 图像矩阵或 raw bytes)
            confidence_threshold: 置信度过滤阈值 (0.0~1.0)
            roi: 可选 ROI 感兴趣渲染检索区域

        Returns:
            list[OcrResult]: 识别出的文本结果列表
        """
        img_bgr, offset_x, offset_y = self._prepare_image_and_offset(scene, roi)
        app = self._get_ocr_app()

        try:
            ocr_output = app.ocr(img_bgr, cls=self.use_angle_cls)
        except Exception as e:
            raise OcrFailedError(f"PaddleOCR 识别过程发生异常: {e}") from e

        results: list[OcrResult] = []
        if not ocr_output or ocr_output[0] is None:
            return results

        lines = ocr_output[0] if isinstance(ocr_output, list) else []

        for line in lines:
            if not line or len(line) < 2:
                continue

            box_raw, (text, conf) = line[0], line[1]
            conf_val = float(conf)

            if conf_val < confidence_threshold:
                continue

            # 转换为 4 个关键角点 (Point) 并叠加 ROI 坐标偏移
            box_points: list[Point] = []
            xs: list[int] = []
            ys: list[int] = []

            for pt in box_raw:
                px = int(round(float(pt[0]))) + offset_x
                py = int(round(float(pt[1]))) + offset_y
                box_points.append(Point(x=px, y=py))
                xs.append(px)
                ys.append(py)

            if len(box_points) != 4 or not xs or not ys:
                continue

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max(1, max_x - min_x)
            height = max(1, max_y - min_y)

            rect = Region(x=min_x, y=min_y, width=width, height=height)
            points_tuple = (box_points[0], box_points[1], box_points[2], box_points[3])

            results.append(
                OcrResult(
                    text=str(text),
                    confidence=conf_val,
                    rect=rect,
                    box_points=points_tuple,
                )
            )

        return results

    @override
    def find_text(
        self,
        scene: MatLike,
        target_text: str,
        confidence_threshold: float = 0.5,
        exact_match: bool = False,
        roi: Region | None = None,
    ) -> OcrResult | None:
        """同步在场景图中检索特定的目标文本。

        Args:
            scene: 输入图像
            target_text: 目标检索文本关键字
            confidence_threshold: 最小置信度阈值
            exact_match: 是否要求精确全等匹配 (True 为完全一致，False 为模糊包含)
            roi: 可选 ROI 检索区域

        Returns:
            OcrResult | None: 匹配到的文本结果或 None
        """
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
