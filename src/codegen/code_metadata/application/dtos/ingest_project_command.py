from pydantic import BaseModel


class IngestProjectCommand(BaseModel):
    """将一个 bounded context 下的目录结构扫描入库为 CodeNode 图。"""

    prefix: str
