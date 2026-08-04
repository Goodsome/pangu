"""注入结果 DTO。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class InjestionResult(BaseModel):
    """一次注入任务的执行结果汇总。"""

    total: int = Field(..., ge=0, description="待注入记录总数")
    succeeded: int = Field(..., ge=0, description="成功注入条数")
    failed: int = Field(..., ge=0, description="失败条数")
    errors: list[str] = Field(default_factory=list, description="失败详情列表")
