from typing import Annotated

from dependency_injector.wiring import Provide, inject
from typer import Argument

from foundation.message_bus.message_bus import BaseMessageBus
from code_structure.application.commands.move_class import MoveClassCommand
from foundation.common_types.fqns.fqn import ClassFqn, ModuleFqn


@inject
def _move_class(
    cmd: MoveClassCommand,
    message_bus: BaseMessageBus = Provide["code_structure_container.message_bus"],
) -> None:
    """
    执行 MoveClass 命令
    """
    message_bus.handle(cmd)


def move_class(
    class_fqn: Annotated[
        str, Argument(help="要移动的类的完全限定名 (e.g., module.path.ClassName)")
    ],
    module_fqn: Annotated[
        str, Argument(help="目标模块的完全限定名 (e.g., target.module.path)")
    ],
) -> None:
    """
    将指定的类移动到新的模块中
    """
    # 将字符串转换为值对象
    class_fqn_obj = ClassFqn(class_fqn)
    module_fqn_obj = ModuleFqn(module_fqn)

    # 组装 Command 对象
    cmd = MoveClassCommand(
        class_fqn=class_fqn_obj,
        module_fqn=module_fqn_obj,
    )
    _move_class(cmd)
