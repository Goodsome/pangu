from enum import IntEnum


class EquipmentSlot(IntEnum):
    """装备槽位代码 (helltides/getRun 的 slot 字段, 暴雪 SNO 槽位数值)。"""

    HELM = 288
    CHEST_ARMOR = 304
    OFF_HAND = 320
    WEAPON = 336
    GLOVES = 352
    BOOTS = 384
    PANTS = 400
    RING_1 = 416
    RING_2 = 432
    AMULET = 448
    TWO_HANDED_WEAPON_1 = 465
    TWO_HANDED_WEAPON_2 = 466
    ONE_HANDED_WEAPON_1 = 467
    ONE_HANDED_WEAPON_2 = 468
    RANGED_WEAPON = 469
