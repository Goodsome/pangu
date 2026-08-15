from pydantic import BaseModel

from d4_types.enums.player_class import PlayerClass


class EntryFilter(BaseModel):
    """榜单查询条件；player_class 为 None 时返回全部职业。"""

    player_class: PlayerClass | None = None
