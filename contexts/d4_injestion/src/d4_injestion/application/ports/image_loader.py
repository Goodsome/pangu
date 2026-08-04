"""图片加载端口：将截图文件路径加载为图像矩阵 (ndarray)。

path -> ndarray 的转换在此端口定义、由 infrastructure 适配器实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from cv_engine.models import MatLike


class ImageLoader(ABC):
    """截图文件路径 -> 图像矩阵加载器端口。"""

    @abstractmethod
    def load(self, path: Path) -> MatLike:
        """加载截图文件为 BGR 三通道 ndarray 矩阵。

        Args:
            path: 截图文件路径。
        """
        ...
