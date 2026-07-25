"""基于 PaddleOCR 的图像文字识别与定位后端实现。"""

from dataclasses import dataclass, field
import logging
from typing import Any, override

from cv_engine.backends.base import BaseOcrEngine
from cv_engine.exceptions import OcrFailedError, OcrInitError
from cv_engine.models import MatLike, OcrResult, Point, Region

logger = logging.getLogger(__name__)


@dataclass
class PaddleOcrEngine(BaseOcrEngine):
    """基于 PaddleOCR 的文字识别与空间定位引擎后端。

    提供从图像中识别中文/英文文本及精准定位位置外接矩形与中心坐标的能力。
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
            init_kwargs: dict[str, Any] = {"lang": self.lang}
            init_kwargs["device"] = "gpu" if self.use_gpu else "cpu"
            init_kwargs["use_textline_orientation"] = self.use_angle_cls

            try:
                self._ocr_app = PaddleOCR(**init_kwargs)
            except ValueError, TypeError:
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
        """同步识别场景中全部文本内容及其所在位置几何信息。"""
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
