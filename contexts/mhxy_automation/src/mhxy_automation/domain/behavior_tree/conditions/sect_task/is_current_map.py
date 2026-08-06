from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class IsCurrentMap(Condition):
    map_names: list[str]
    
    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        current_map = await blackboard.client.main_hud.get_current_map()
        if current_map in self.map_names:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
