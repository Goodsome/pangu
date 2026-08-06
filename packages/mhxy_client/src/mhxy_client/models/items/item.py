from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Item:
    __store__: ClassVar[dict[str, Item]]
    
    name: str

    def __post_init__(self):
        if not hasattr(self.__class__, "__store__"):
            self.__class__.__store__ = {}
        self.__class__.__store__[self.name] = self
