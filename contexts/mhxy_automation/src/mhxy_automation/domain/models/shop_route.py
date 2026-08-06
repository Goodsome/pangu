from typing import TypedDict


class ShopRoute(TypedDict):
    city_map: str
    shop_map: str
    npc_name: str

ITEM_KNOWLEDGE_DB: dict[str, ShopRoute] = {
    "高级宠物口粮": {
        "city_map": "长安城",
        "shop_map": "杂货铺",
        "npc_name": "",
    },
}