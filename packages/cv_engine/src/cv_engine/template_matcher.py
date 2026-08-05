"""OpenCV 模板匹配器核心实现层。"""

import asyncio
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import override

import cv2
import numpy as np

from cv_engine.constants import (
    DEFAULT_MATCH_THRESHOLD,
    DEFAULT_NMS_IOU_THRESHOLD,
    MatchMode,
)
from cv_engine.exceptions import (
    InvalidImageError,
    MatchFailedError,
    TemplateNotFoundError,
)
from cv_engine.interfaces import ITemplateMatcher
from cv_engine.models import MatLike, MatchResult, Region

logger = logging.getLogger(__name__)


def get_opencv_match_modes() -> dict[MatchMode, int]:
    """获取 OpenCV 匹配模式常量映射表。"""
    return {
        MatchMode.CCOEFF_NORMED: getattr(cv2, "TM_CCOEFF_NORMED", 5),
        MatchMode.CCORR_NORMED: getattr(cv2, "TM_CCORR_NORMED", 3),
        MatchMode.SQDIFF_NORMED: getattr(cv2, "TM_SQDIFF_NORMED", 1),
    }

def load_template_with_mask(template_path: Path | str) -> tuple[np.ndarray, np.ndarray]:
    """
    加载模板图片，保留彩色信息，并提取 Alpha 通道作为掩码。
    """
    path_obj = Path(template_path)
    path_key = str(path_obj.resolve())

    # 使用 IMREAD_UNCHANGED 保留可能存在的 Alpha 通道
    img = cv2.imread(path_key, cv2.IMREAD_UNCHANGED)
    if img is None or img.size == 0:
        raise ValueError(f"无法解析模板图片: {template_path}")

    mask = None
    if img.ndim == 3 and img.shape[2] == 4:
        # 分离出 BGRA 通道
        b, g, r, a = cv2.split(img)
        img_bgr = cv2.merge((b, g, r))
        mask = a # 使用 Alpha 通道作为掩码
        return img_bgr, mask

    raise ValueError("不支持的模板图像格式类型")

def _normalize_scene_bgr(scene: np.ndarray) -> np.ndarray:
    """
    将场景输入图像规范化解析为 3D BGR 三通道矩阵。
    """
    if scene.size == 0:
        raise ValueError("场景图像矩阵 size 为 0")

    if scene.ndim == 2:
        return cv2.cvtColor(scene, cv2.COLOR_GRAY2BGR)
    if scene.ndim == 3:
        channels = int(scene.shape[2])
        if channels == 4:
            return cv2.cvtColor(scene, cv2.COLOR_BGRA2BGR)
        if channels == 3:
            return scene

    raise ValueError(f"不支持的场景图像格式类型")

@dataclass
class TemplateMatcher(ITemplateMatcher):
    """基于 OpenCV 的模板匹配器。

    支持内存模板缓存、灰度自动归一化、ROI 检索裁剪、单点/多点精准匹配以及 NMS 重叠去重。
    """

    _template_cache: dict[str, np.ndarray] = field(default_factory=dict, repr=False)

    @override
    def load_template(self, template_path: Path | str) -> np.ndarray:
        """加载并缓存模板图片（归一化为单通道灰度图）。

        Args:
            template_path: 模板图片文件路径

        Returns:
            np.ndarray: 灰度图像矩阵

        Raises:
            TemplateNotFoundError: 文件不存在或读取失败时抛出
        """
        path_obj = Path(template_path)
        path_key = str(path_obj.resolve())

        if path_key in self._template_cache:
            return self._template_cache[path_key]

        if not path_obj.exists():
            raise TemplateNotFoundError(f"模板图片未找到: {template_path}")

        img = cv2.imread(path_key, cv2.IMREAD_GRAYSCALE)
        if img is None or img.size == 0:
            raise TemplateNotFoundError(f"无法解析模板图片文件数据: {template_path}")

        self._template_cache[path_key] = img
        return img

    @override
    def match_masked_template(
        self,
        scene: MatLike,
        template: Path,
        roi: Region | None = None,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
    ) -> MatchResult | None:
        template_bgr, mask = load_template_with_mask(template)
        scene_normalized = _normalize_scene_bgr(scene)
        roi_img, offset_x, offset_y = self._crop_roi(scene_normalized, template_bgr, roi)
        result = self._match_masked_core(
            roi_img=roi_img,
            template_bgr=template_bgr,
            mask=mask,
        )
        return self._get_match_result(result, template_bgr, threshold, offset_x, offset_y, mode=MatchMode.CCORR_NORMED)

    @override
    def match_best(
        self,
        scene: MatLike,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
    ) -> MatchResult | None:
        """查找场景图像中单目标最佳匹配点（得分最高点）。

        Args:
            scene: 输入场景图 (支持 OpenCV MatLike 或 raw bytes)
            template: 模板图 (支持 Path、路径字符串或 MatLike 矩阵)
            threshold: 最低匹配相似度阈值
            roi: 可选检索感兴趣区域
            mode: 匹配计算模式

        Returns:
            MatchResult | None: 最佳匹配结果或 None (未达到阈值)
        """
        scene_gray = self._normalize_scene(scene)
        template_gray, t_name = self._resolve_template(template)

        roi_img, offset_x, offset_y = self._crop_roi(scene_gray, template_gray, roi)
        res = self._match_core(roi_img, template_gray, mode)

        return self._get_match_result(res, template_gray, threshold, offset_x, offset_y, mode)


    def _get_match_result(
        self, 
        res: np.ndarray,
        template_gray: np.ndarray,
        threshold: float,
        offset_x: int,
        offset_y: int,
        mode: MatchMode
    ) -> MatchResult | None:
        cv_mode = get_opencv_match_modes().get(mode, 5)
        th, tw = int(template_gray.shape[0]), int(template_gray.shape[1])
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if cv_mode == getattr(cv2, "TM_SQDIFF_NORMED", 1):
            score = float(1.0 - min_val)
            best_loc = min_loc
        else:
            score = float(max_val)
            best_loc = max_loc

        if score >= threshold:
            abs_x = offset_x + int(best_loc[0])
            abs_y = offset_y + int(best_loc[1])
            return MatchResult(
                score=score,
                rect=Region(x=abs_x, y=abs_y, width=tw, height=th),
                template_name=None,
            )

        return None

    @override
    def match_multi(
        self,
        scene: MatLike,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
        nms_threshold: float = DEFAULT_NMS_IOU_THRESHOLD,
    ) -> list[MatchResult]:
        """查找场景图像中所有符合阈值的多目标匹配列表（使用 NMS 过滤重叠结果）。

        Args:
            scene: 输入场景图
            template: 模板图
            threshold: 匹配相似度阈值
            roi: 可选 ROI 区域
            mode: 匹配计算模式
            nms_threshold: NMS 重叠框 IoU 过滤阈值

        Returns:
            list[MatchResult]: 匹配结果列表 (按得分从高到低排序)
        """
        scene_gray = self._normalize_scene(scene)
        template_gray, t_name = self._resolve_template(template)

        roi_img, offset_x, offset_y = self._crop_roi(scene_gray, template_gray, roi)
        res = self._match_core(roi_img, template_gray, mode)

        cv_mode = get_opencv_match_modes().get(mode, 5)
        th, tw = int(template_gray.shape[0]), int(template_gray.shape[1])

        if cv_mode == getattr(cv2, "TM_SQDIFF_NORMED", 1):
            score_matrix = 1.0 - res
        else:
            score_matrix = res

        loc = np.where(score_matrix >= threshold)
        pts = list(zip(*loc[::-1], strict=False))

        if not pts:
            return []

        boxes: list[list[int]] = []
        scores: list[float] = []

        for pt in pts:
            x, y = int(pt[0]), int(pt[1])
            sc = float(score_matrix[y, x])
            boxes.append([x, y, tw, th])
            scores.append(sc)

        indices = cv2.dnn.NMSBoxes(
            bboxes=boxes,
            scores=scores,
            score_threshold=threshold,
            nms_threshold=nms_threshold,
        )

        results: list[MatchResult] = []
        if len(indices) > 0:
            flattened = np.asarray(indices).flatten()
            for idx in flattened:
                i = int(idx)
                box = boxes[i]
                abs_x = offset_x + box[0]
                abs_y = offset_y + box[1]
                results.append(
                    MatchResult(
                        score=scores[i],
                        rect=Region(x=abs_x, y=abs_y, width=tw, height=th),
                        template_name=t_name,
                    )
                )

        results.sort(key=lambda item: item.score, reverse=True)
        return results

    @override
    async def async_match_best(
        self,
        scene: MatLike,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
    ) -> MatchResult | None:
        """异步查找单目标最佳匹配。"""
        return await asyncio.to_thread(
            self.match_best, scene, template, threshold, roi, mode
        )

    @override
    async def async_match_multi(
        self,
        scene: MatLike,
        template: Path | str | MatLike,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
        roi: Region | None = None,
        mode: MatchMode = MatchMode.CCOEFF_NORMED,
        nms_threshold: float = DEFAULT_NMS_IOU_THRESHOLD,
    ) -> list[MatchResult]:
        """异步查找多目标匹配。"""
        return await asyncio.to_thread(
            self.match_multi, scene, template, threshold, roi, mode, nms_threshold
        )

    @override
    def clear_cache(self) -> None:
        """清理已缓存的模板矩阵。"""
        self._template_cache.clear()

    # ---------------------------------------------------------------------------
    # 内部辅助方法
    # ---------------------------------------------------------------------------
    def _normalize_scene(self, scene: MatLike) -> np.ndarray:
        """将场景输入图像规范化解析为 2D 灰度单通道矩阵。"""
        if isinstance(scene, np.ndarray):
            if scene.size == 0:
                raise InvalidImageError("场景图像矩阵 size 为 0")

            if scene.ndim == 2:
                return scene
            if scene.ndim == 3:
                channels = int(scene.shape[2])
                if channels == 4:
                    return cv2.cvtColor(scene, cv2.COLOR_BGRA2GRAY)
                if channels == 3:
                    return cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
                if channels == 1:
                    return scene[:, :, 0]

        raise InvalidImageError(f"不支持的场景图像格式类型: {type(scene)}")

    def _resolve_template(
        self, template: Path | str | MatLike
    ) -> tuple[np.ndarray, str | None]:
        """解析并转换模板矩阵与名称。"""
        if isinstance(template, (Path, str)):
            t_path = Path(template)
            img = self.load_template(t_path)
            return img, t_path.stem

        if isinstance(template, np.ndarray):
            if template.size == 0:
                raise TemplateNotFoundError("传入的模板 np.ndarray 为空")
            if template.ndim == 2:
                return template, None
            if template.ndim == 3:
                channels = int(template.shape[2])
                if channels == 4:
                    return cv2.cvtColor(template, cv2.COLOR_BGRA2GRAY), None
                if channels == 3:
                    return cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), None
                return template[:, :, 0], None

        raise TemplateNotFoundError(f"未知的模板类型: {type(template)}")

    def _crop_roi(
        self, scene_gray: np.ndarray, template_gray: np.ndarray, roi: Region | None
    ) -> tuple[np.ndarray, int, int]:
        """处理 ROI 剪裁与边界容错控制。"""
        sh, sw = int(scene_gray.shape[0]), int(scene_gray.shape[1])
        th, tw = int(template_gray.shape[0]), int(template_gray.shape[1])

        if roi is None:
            return scene_gray, 0, 0

        # ROI 坐标边界限制
        x1 = max(0, min(roi.x, sw))
        y1 = max(0, min(roi.y, sh))
        x2 = max(0, min(roi.right, sw))
        y2 = max(0, min(roi.bottom, sh))

        roi_w = x2 - x1
        roi_h = y2 - y1

        # 尺寸容错防护
        if tw > roi_w or th > roi_h:
            logger.warning(
                "[TemplateMatcher] 模板尺寸 (%dx%d) 超出 ROI 检索区域 (%dx%d)，退回全图检索",
                tw,
                th,
                roi_w,
                roi_h,
            )
            return scene_gray, 0, 0

        cropped = scene_gray[y1:y2, x1:x2]
        return cropped, x1, y1

    def _match_core(
        self, roi_img: np.ndarray, template_gray: np.ndarray, mode: MatchMode
    ) -> np.ndarray:
        """执行底层 OpenCV 匹配算法。"""
        try:
            cv_mode = get_opencv_match_modes().get(mode, getattr(cv2, "TM_CCOEFF_NORMED", 5))
            return cv2.matchTemplate(roi_img, template_gray, cv_mode)
        except Exception as e:
            raise MatchFailedError(f"OpenCV matchTemplate 计算失败: {e}") from e

    def _match_masked_core(
        self, roi_img: np.ndarray, template_bgr: np.ndarray, mask: np.ndarray,
    ) -> np.ndarray:
        cv_mode = cv2.TM_CCORR_NORMED
        return cv2.matchTemplate(roi_img, template_bgr, cv_mode, mask=mask)
