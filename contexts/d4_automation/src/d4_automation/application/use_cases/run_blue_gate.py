import asyncio
from dataclasses import dataclass

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.behavior_tree.open_or_close_socical import OpenOrCloseSocial
from d4_automation.domain.enums.node_status import NodeStatus
from d4_client import create_d4_client_by_index


@dataclass
class RunBlueGate:

    async def execute(self, window_index: int, cancel_event: asyncio.Event):
        d4_client = create_d4_client_by_index(window_index)

        async with d4_client:
            blackboard = Blackboard(
                client=d4_client,
                current_panel=d4_client.main_hud,
            )
            behavior_tree = OpenOrCloseSocial()

            try:
                while not cancel_event.is_set():
                    await d4_client.begin_frame()
                    status = await behavior_tree.tick(blackboard)
                    if status == NodeStatus.SUCCESS:
                        pass
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                pass
