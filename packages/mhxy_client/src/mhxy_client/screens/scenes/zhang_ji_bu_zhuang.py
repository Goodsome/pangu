from dataclasses import dataclass

from mhxy_client.models.npcs.npc import Npc
from mhxy_client.screens.dialogs.base import NpcDialog
from mhxy_client.screens.scenes.base_scene import Scene


@dataclass
class ZhangJiBuZhuangScene(Scene):
    screen_name: str = "张记布庄"
