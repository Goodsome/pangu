from dataclasses import dataclass

from d4_client import D4Client, D4Panel


@dataclass
class Blackboard:
    client: D4Client
    current_panel: D4Panel

    def update_panel(self, panel: D4Panel) -> None:
        self.current_panel = panel
