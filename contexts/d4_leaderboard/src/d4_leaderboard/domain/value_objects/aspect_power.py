from typing import ClassVar
from foundation.building_blocks.value_object import ValueObject
from pydantic import ConfigDict, Field


class AspectPower(ValueObject):
    """传奇威能 / 专属特效值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int = Field(..., description="威能/特效 ID")
    codename: str = Field(..., description="威能程序代号")
    category: int = Field(default=0, description="威能类别代码")
    is_transfigured: bool = Field(default=False, description="是否变异")
