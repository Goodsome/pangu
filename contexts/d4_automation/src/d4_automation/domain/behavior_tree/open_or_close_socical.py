from dataclasses import dataclass, field
from d4_automation.domain.behavior_tree.actions.close_social import CloseSocial
from d4_automation.domain.behavior_tree.actions.open_social import OpenSocial
from d4_automation.domain.behavior_tree.conditions.is_panel_active import IsPanelActive
from d4_automation.domain.behavior_tree.core import BaseNode, Selector, Sequence
from d4_client import MainHUD, SocialPanel


@dataclass
class OpenOrCloseSocial(Selector):
    children: list[BaseNode] = field(init=False)

    def __post_init__(self):
        open_social_in_main_hud = Sequence(
            children=[
                IsPanelActive(expected_panel=MainHUD),
                OpenSocial(),
            ]
        )
        close_social_in_social_panel = Sequence(
            children=[
                IsPanelActive(expected_panel=SocialPanel),
                CloseSocial(),
            ]
        )
        self.children = [
            open_social_in_main_hud,
            close_social_in_social_panel,
        ]
