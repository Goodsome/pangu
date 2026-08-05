from dataclasses import dataclass

from mhxy_client.models.items.item import Item


@dataclass
class BuXie(Item):
    name: str = "布鞋"
    grid_location: tuple[int, int] = (0, 2)
    npc: str = "zai"
    