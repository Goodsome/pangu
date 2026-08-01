from enum import StrEnum
from typing import Any


class PlayerClass(StrEnum):
    BARBARIAN = "BARBARIAN"
    DRUID = "DRUID"
    NECROMANCER = "NECROMANCER"
    ROGUE = "ROGUE"
    SORCERER = "SORCERER"
    SPIRITBORN = "SPIRITBORN"
    PALADIN = "PALADIN"
    WARLOCK = "WARLOCK"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        if isinstance(value, str):
            upper_val = value.upper()
            for member in cls:
                if member.value == upper_val:
                    return member
        return None
