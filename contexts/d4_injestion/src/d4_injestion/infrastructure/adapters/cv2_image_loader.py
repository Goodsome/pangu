"""基于 cv2.imread 的图片加载适配器: path -> ndarray。

「path -> ndarray」的物理实现唯一落点: 此适配器将截图文件读入 BGR 三通道
ndarray 矩阵, 供 OcrScanner 消费。domain/application 层只依赖 ImageLoader 端口。
"""

from __future__ import annotations

from pathlib import Path
from typing import override

import cv2  # noqa: F401  # 实现 load() 时调用 cv2.imread

from cv_engine.models import MatLike

from d4_injestion.application.ports.image_loader import ImageLoader


class Cv2ImageLoader(ImageLoader):
    """使用 OpenCV (cv2.imread) 加载截图文件的适配器。"""

    @override
    def load(self, path: Path) -> MatLike:
        """读取截图文件为 BGR 三通道 ndarray。

        Args:
            path: 截图文件路径。

        Raises:
            FileNotFoundError: 文件不存在或无法解码。
        """
        ...
