from dataclasses import dataclass
from typing import Literal

from client_core import RelativeRegion
from mhxy_client.models.map import Map
from mhxy_client.models.npcs.npc import Npc


@dataclass
class FuZhuangDianLaoBan(Npc):
    name: str = "服装店老板"
    map: Literal[Map.CHANG_AN] = Map.CHANG_AN
    map_location: RelativeRegion = RelativeRegion(x=0.5517, y=0.6923, width=0.0837, height=0.0196)
    scene_location: RelativeRegion = RelativeRegion(x=0.5924, y=0.27, width=0.0665, height=0.1463)
    house_name: str = "张记布庄"