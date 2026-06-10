from pydantic import BaseModel


class IngestProjectResult(BaseModel):
    """IngestProject 命令的执行结果。"""

    nodes_created: int
    edges_created: int
    nodes_deleted: int
