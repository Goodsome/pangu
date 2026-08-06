"""基于 RapidOCR (rapidocr-onnxruntime) 的图像文字识别与定位后端实现。"""

from dataclasses import dataclass, field
import logging
from typing import Any, override

from cv_engine.backends.base import BaseOcrEngine
from cv_engine.exceptions import OcrFailedError, OcrInitError
from cv_engine.models import MatLike, OcrResult, Point, Region

logger = logging.getLogger(__name__)


@dataclass
class RapidOcrEngine(BaseOcrEngine):
    """基于 RapidOCR (rapidocr-onnxruntime) 的文字识别与空间定位引擎后端。

    支持 Python 3.14+ 高版本环境，使用 ONNX Runtime 进行开箱即用的推理。
    """

    lang: str = "ch"
    use_gpu: bool = False
    det_use_cuda: bool = False
    rec_use_cuda: bool = False

    _ocr_app: Any = field(default=None, repr=False)

    def _get_ocr_app(self) -> Any:
        """获取或延迟初始化 RapidOCR 识别实例。"""
        if self._ocr_app is not None:
            return self._ocr_app

        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as e:
            raise OcrInitError(
                "未找到 rapidocr-onnxruntime 依赖包，请先安装: pip install rapidocr-onnxruntime"
            ) from e

        try:
            use_cuda = self.use_gpu or self.det_use_cuda or self.rec_use_cuda
            self._ocr_app = RapidOCR(
                det_use_cuda=use_cuda,
                rec_use_cuda=use_cuda,
            )
            return self._ocr_app
        except Exception as e:
            raise OcrInitError(f"初始化 RapidOCR 引擎失败: {e}") from e

    @override
    def get_text(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
    ) -> str | None:
        """同步获取场景中的全部文本内容。"""
        img_bgr, offset_x, offset_y = self._prepare_image_and_offset(scene, roi)
        app = self._get_ocr_app()
        ocr_output, _ = app(img_bgr, use_det=False)
        
        if not ocr_output:
            return None
        
        return ocr_output[0][0]

    
    @override
    def ocr(
        self,
        scene: MatLike,
        confidence_threshold: float = 0.5,
        roi: Region | None = None,
        save_debug_img: bool = False,
        debug_dir: str = "screenshots",
    ) -> list[OcrResult]:
        """同步识别场景中全部文本内容及其所在位置几何信息。"""
        import cv2
        import pathlib
        import time
        img_bgr, offset_x, offset_y = self._prepare_image_and_offset(scene, roi)
        app = self._get_ocr_app()
    
        # 1. 图像放大预处理（提升小图识别率）
        h, w = img_bgr.shape[:2]
        scale = 2 if h < 30 else 1.0
        
        if scale != 1.0:
            processed_img = cv2.resize(img_bgr, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        else:
            processed_img = img_bgr.copy()
    
        # 2. 执行识别
        try:
            ocr_output, _ = app(processed_img)
        except Exception as e:
            raise OcrFailedError(f"RapidOCR 识别过程发生异常: {e}") from e
    
        results: list[OcrResult] = []
        
        if not ocr_output:
            return results
    
        # 3. 保存调试图片逻辑
        if save_debug_img:
            save_path = pathlib.Path(debug_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            timestamp = int(time.time() * 1000)
    
            # 保存送入模型前的图像（包含放大后的结果）
            cv2.imwrite(str(save_path / f"ocr_{timestamp}_input.png"), processed_img)
    
    
        # 4. 解析识别结果并还原坐标
        for line in ocr_output:
            logger.info(f"识别结果: {line}")
            if not line or len(line) < 3:
                continue
    
            box_raw, text, conf = line[0], line[1], line[2]
            conf_val = float(conf)
    
            if conf_val < confidence_threshold:
                continue
    
            box_points: list[Point] = []
            xs: list[int] = []
            ys: list[int] = []
    
            for pt in box_raw:
                # 除以 scale 还原回原图坐标
                px = int(round(float(pt[0]) / scale)) + offset_x
                py = int(round(float(pt[1]) / scale)) + offset_y
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