from dataclasses import dataclass, field
import time
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.behavior_tree.core import Action
from mhxy_automation.domain.enums.node_status import NodeStatus


@dataclass
class ReturnShiMeng(Action):

    running_time: float = 1
    start_time: float = field(default=0, init=False)

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:

        now = time.monotonic()
        if now - self.start_time < self.running_time:
            return NodeStatus.RUNNING
            
        await blackboard.client.main_hud.return_shi_meng()
        self.start_time = now
        
        return NodeStatus.SUCCESS
    
