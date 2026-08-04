"""OCR 文本识别块值对象。

与 cv_engine.OcrResult 解耦的领域模型，使 domain 层不直接依赖 cv_engine。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import ConfigDict, Field

from d4_injestion.domain.value_objects.text_region import TextRegion
from foundation.building_blocks.value_object import ValueObject


class OcrTextBlock(ValueObject):
    """单块 OCR 识别文本及其置信度与位置。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    text: str = Field(..., description="识别到的文本内容")
    confidence: float = Field(..., ge=0.0, le=1.0, description="识别置信度")
    region: TextRegion = Field(..., description="文本所在矩形区域")
