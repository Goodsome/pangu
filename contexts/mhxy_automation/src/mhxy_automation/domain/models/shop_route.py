from dataclasses import dataclass

from mhxy_automation.domain.models.shop import SHOP_DB


@dataclass
class ShopRoute:
    city_map: str
    shop: str
    npc_name: str
    item_location: tuple[int, int]

    @classmethod
    def from_item_name(cls, item_name: str):
        for shop in SHOP_DB:
            if item_name in shop.items:
                return cls(
                    city_map=shop.city,
                    shop=shop.house,
                    npc_name=shop.name,
                    item_location=shop.get_item_location(item_name),
                )
        raise ValueError(f"Item {item_name} not found in any shop")

ITEM_KNOWLEDGE_DB: dict[str, ShopRoute] = {}
#     "高级宠物口粮": {
#         "city_map": "长安城",
#         "shop": "南北杂货店",
#         "npc_name": "杂货店老板",
#         "item_location": (0, 4),
#     },
#     "红缨枪": {
#         "city_map": "长安城",
#         "shop": "万胜武器店",
#         "npc_name": "武器店掌柜",
#         "item_location": (0, 1),
#     },
#     "黄铜圈": {
#         "city_map": "长安城",
#         "shop": "万胜武器店",
#         "npc_name": "武器店掌柜",
#         "item_location": (2, 0),
#     },
#     "鬼切草": {
#         "city_map": "长安城",
#         "shop": "回春堂",
#         "npc_name": "药店老板",
#         "item_location": (0, 3),
#     },
#     "佛手": {
#         "city_map": "长安城",
#         "shop": "回春堂",
#         "npc_name": "药店老板",
#         "item_location": (0, 4),
#     },
#     "布鞋": {
#         "city_map": "长安城",
#         "shop": "张记布庄",
#         "npc_name": "服装店老板",
#         "item_location": (0, 2),
#     },
# }