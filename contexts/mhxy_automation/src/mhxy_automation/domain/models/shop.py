from dataclasses import dataclass

from mhxy_automation.domain.enums.names import CityName, HouseName

SHOP_ROWS = 4
SHOP_COLS = 5


@dataclass
class Shop:
    name: str
    city: str
    house: str
    items: list[str]

    def get_item_location(self, item_name: str) -> tuple[int, int]:
        if item_name not in self.items:
            raise ValueError(f"Item {item_name} not found in shop")
        item_index = self.items.index(item_name)
        return item_index // SHOP_COLS, item_index % SHOP_COLS


SHOP_DB = [
    Shop(
        name="武器店掌柜",
        city=CityName.CHANG_AN,
        house=HouseName.WANG_SHENG_WU_QI_DIAN,
        items=[
            "折扇",
            "红缨枪",
            "牛皮鞭",
            "铁爪",
            "松木锤",
            "双短剑",
            "青铜短剑",
            "柳叶刀",
            "青铜斧",
            "五色缎带",
            "黄铜圈",
            "细木棒",
        ],
    ),
    Shop(
        name="福寿店老板",
        city=CityName.CHANG_AN,
        house="平安福寿店",
        items=["香", "蜡烛", "黄纸"],
    ),
    Shop(
        name="药店老板",
        city=CityName.CHANG_AN,
        house="回春堂",
        items=[
            "香叶",
            "百色花",
            "草果",
            "鬼切草",
            "佛手",
            "山药",
            "月见草",
            "九香虫",
            "七叶莲",
        ],
    ),
    Shop(
        name="服装店老板",
        city=CityName.CHANG_AN,
        house="张记布庄",
        items=[
            "面具",
            "簪子",
            "布鞋",
            "布裙",
            "梅花簪子",
            "五彩裙",
            "鳞甲",
            "马靴",
            "方巾",
            "布衣",
        ],
    ),
]
