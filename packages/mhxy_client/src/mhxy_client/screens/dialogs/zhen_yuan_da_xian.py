from dataclasses import dataclass

from mhxy_client.screens.dialogs.base import NpcDialog


@dataclass
class ZhenYuanDaXianDialog(NpcDialog):
    npc_name: str = "镇元大仙"
    