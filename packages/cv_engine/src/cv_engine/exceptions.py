"""CV 引擎异常定义层。

预定义视觉计算、模板匹配与 OCR 文本识别异常。
"""

from typing import override


class CVEngineError(Exception):
    """cv_engine 库基础异常类型。"""

    message: str
    code: int | None

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    @override
    def __str__(self) -> str:
        if self.code is not None:
            return f"[{self.code}] {self.message}"
        return self.message


class TemplateNotFoundError(CVEngineError):
    """模板文件未找到或图片数据不可读异常。"""


class InvalidImageError(CVEngineError):
    """输入的场景或图像数据格式无效异常。"""


class MatchFailedError(CVEngineError):
    """模板匹配过程发生异常。"""


class OCRError(CVEngineError):
    """OCR 引擎错误基类。"""


class OcrInitError(OCRError):
    """PaddleOCR 初始化或依赖库缺少异常。"""


class OcrFailedError(OCRError):
    """OCR 文本识别计算异常。"""
