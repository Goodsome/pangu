from dataclasses import dataclass, field

from client_core import Window
from mhxy_client.screens.dialogs.guan_yin_jie_jie import GuanYinJieJie


@dataclass
class Dialogs:
    window: Window
    guan_yin_jie_jie: GuanYinJieJie = field(init=False)

    def __post_init__(self):
        self.guan_yin_jie_jie = GuanYinJieJie(window=self.window)