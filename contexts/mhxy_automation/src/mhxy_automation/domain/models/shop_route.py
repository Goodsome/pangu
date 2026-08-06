from typing import TypedDict


class ShopRoute(TypedDict):
    city_map: str
    shop: str
    npc_name: str
    item_location: tuple[int, int]

ITEM_KNOWLEDGE_DB: dict[str, ShopRoute] = {
    "高级宠物口粮": {
        "city_map": "长安城",
        "shop": "南北杂货店",
        "npc_name": "杂货店老板",
        "item_location": (0, 4),
    },
}