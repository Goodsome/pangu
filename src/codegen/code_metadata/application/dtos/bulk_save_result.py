from pydantic import BaseModel


class BulkSaveResult(BaseModel):
    """save_nodes_bulk 的执行结果。"""

    nodes_upserted: int
    edges_created: int
