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
    "红缨枪": {
        "city_map": "长安城",
        "shop": "万胜武器店",
        "npc_name": "武器店掌柜",
        "item_location": (0, 1),
    },
    "黄铜圈": {
        "city_map": "长安城",
        "shop": "万胜武器店",
        "npc_name": "武器店掌柜",
        "item_location": (2, 0),
    },
    "鬼切草": {
        "city_map": "长安城",
        "shop": "回春堂",
        "npc_name": "药店老板",
        "item_location": (0, 3),
    },
    "佛手": {
        "city_map": "长安城",
        "shop": "回春堂",
        "npc_name": "药店老板",
        "item_location": (0, 4),
    },
    "布鞋": {
        "city_map": "长安城",
        "shop": "张记布庄",
        "npc_name": "服装店老板",
        "item_location": (0, 2),
    },
}