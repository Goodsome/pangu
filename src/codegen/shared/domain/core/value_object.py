from typing import ClassVar
from pydantic import BaseModel
from pydantic import ConfigDict


class ValueObject(BaseModel):
    """值对象基类 特征： 1. 不可变（frozen=True） 2. 相等性基于所有属性值 3. 无唯一标识"""

    # model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
