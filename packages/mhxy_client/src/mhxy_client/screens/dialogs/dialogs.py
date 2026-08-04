from client_core import Window
from mhxy_client.screens.dialogs.guan_yin_jie_jie import GuanYinJieJie
from mhxy_client.screens.dialogs.hui_bei import HuiBeiDialog


class Dialogs:

    def __init__(self, window: Window):
        self.window = window
        self.guan_yin_jie_jie = GuanYinJieJie(window=self.window)
        self.hui_bei = HuiBeiDialog(window=self.window)