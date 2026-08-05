from dataclasses import dataclass

from client_core import RelativeRegion
from mhxy_client.screens.dialogs.base import NpcDialog


@dataclass
class Npc:
    
    name: str
    map_location: RelativeRegion
    scene_location: RelativeRegion
    dialog: type[NpcDialog] = NpcDialog
    