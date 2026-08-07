from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Condition
from mhxy_automation.domain.enums.node_status import NodeStatus

wuzhuang = ["五庄观", "乾坤殿"]
putuo = ["普陀山", "潮音洞"]


@dataclass
class IsInShiMengMap(Condition):
    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        current_map = await blackboard.client.main_hud.get_current_map()
        if blackboard.client.role_id == "39068983":
            map_names = wuzhuang
        else:
            map_names = putuo
        if current_map in map_names:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
