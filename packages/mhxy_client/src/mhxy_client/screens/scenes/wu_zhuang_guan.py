from dataclasses import dataclass

from mhxy_client.screens.scenes.scene import Scene


@dataclass
class WuZhuangGuan(Scene):
    screen_name: str = "五庄观"
    