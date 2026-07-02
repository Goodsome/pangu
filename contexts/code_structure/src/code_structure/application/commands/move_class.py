from dataclasses import dataclass

from code_structure.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.command import Command
from foundation.common_types.fqns.fqn import ClassFqn, ModuleFqn


class MoveClassCommand(Command):
    """
    MoveClass 命令
    """
    class_fqn: ClassFqn
    module_fqn: ModuleFqn


@dataclass
class MoveClassCommandHandler:
    """
    MoveClass 命令处理器代码桩
    """

    def execute(self, cmd: MoveClassCommand, uow: UnitOfWork) -> None:
        """
        执行具体的命令逻辑。
        当前为脚手架阶段，不实现具体业务逻辑。
        """
        ...
