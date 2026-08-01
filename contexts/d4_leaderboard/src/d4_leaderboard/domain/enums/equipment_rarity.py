from enum import StrEnum
from typing import Any


class EquipmentRarity(StrEnum):
    NORMAL = "Normal"
    MAGIC = "Magic"
    RARE = "Rare"
    LEGENDARY = "Legendary"
    UNIQUE = "Unique"
    MYTHIC_UNIQUE = "Mythic Unique"
    MYTHIC = "Mythic"
    SET = "Set"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        if isinstance(value, str):
            lower_val = value.lower().replace(" ", "")
            for member in cls:
                if member.value.lower().replace(" ", "") == lower_val:
                    return member
        return None
