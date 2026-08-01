"""d4_automation 图像 I/O 工具函数。

提供 ImageFrame 异步保存为磁盘文件的通用能力，
供行为树 Action 节点复用。
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import cv2
import numpy as np

from d4_client import ImageFrame

logger = logging.getLogger(__name__)


def _frame_to_bgr(frame: ImageFrame) -> np.ndarray:
    """将 ImageFrame 转换为 cv2 可写的 BGR ndarray。

    ImageFrame.mat 以 BGRA（4通道）或 BGR（3通道）形式存储。
    cv2.imwrite 写 PNG 时支持两者，但统一转为 BGR 更稳定。
    """
    mat = frame.mat  # shape: (H, W, C)
    if frame.channels == 4:
        # BGRA → BGR，丢弃 alpha 通道
        return cv2.cvtColor(mat, cv2.COLOR_BGRA2BGR)
    return mat  # type: ignore[return-value]


async def save_image(frame: ImageFrame, path: Path) -> None:
    """将 ImageFrame 异步保存为 PNG 文件。

    - 自动创建父目录
    - 在线程池中执行 cv2.imwrite，避免阻塞事件循环
    - 写入失败时抛出 RuntimeError

    Args:
        frame: 待保存的图像帧。
        path:  目标文件路径（.png 扩展名）。

    Raises:
        RuntimeError: cv2.imwrite 返回 False（写入失败）。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    bgr = _frame_to_bgr(frame)
    path_str = str(path)

    loop = asyncio.get_running_loop()
    ok: bool = await loop.run_in_executor(None, cv2.imwrite, path_str, bgr)

    if not ok:
        raise RuntimeError(f"[save_image] cv2.imwrite 写入失败: {path}")

    logger.debug("[save_image] 已保存 → %s (%dx%d)", path, frame.width, frame.height)
