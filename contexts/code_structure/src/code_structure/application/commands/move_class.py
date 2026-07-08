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
    MoveClass 命令处理器
    """

    def execute(self, cmd: MoveClassCommand, uow: UnitOfWork) -> None:
        """
        执行具体的命令逻辑：获取聚合根，在领域层中更新模块绑定并移动类，然后保存更新。
        """
        # 1. 获取要移动的类聚合根
        class_symbol = uow.classes.get_by_fqn(cmd.class_fqn)

        # 2. 获取源模块和目标模块聚合根
        source_module = uow.file_modules.get_by_fqn(cmd.class_fqn.module_fqn)
        target_module = uow.file_modules.get_by_fqn(cmd.module_fqn)

        # 3. 领域对象行为编排：将类从旧模块解绑，绑定到目标模块，并执行类本身的移动
        source_module.undefine_class(class_symbol.id)
        target_module.define_class(class_symbol.id)
        class_symbol.move(cmd.module_fqn)

        # 4. 持久化聚合根状态
        uow.classes.save(class_symbol)
        uow.file_modules.save(source_module)
        uow.file_modules.save(target_module)
