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
    Shop(name="武器店掌柜", city=CityName.CHANG_AN, house=HouseName.WANG_SHENG_WU_QI_DIAN, items=[
        "折扇", "红缨枪", "牛皮鞭", "铁爪", "松木锤", "双短剑", 
        "青铜短剑", "柳叶刀", "青铜斧", "五色缎带", "黄铜圈", "细木棒",
    ]),
]
