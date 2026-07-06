# 触发条件与参数校验 (Validation Rules)
在执行代码生成前，必须从主任务/需求方获取以下信息：
1. **所属上下文 (Bounded Context)**：命令所属的模块名称（用于确定文件路径）。
2. **命令名称 (Command Name)**：代表业务意图的动作名称（如 `RemoveModule`）。
3. **参数逻辑 (Parameters)**：命令包含的属性及其对应的领域类型（值对象）。
   - **拦截规则**：如果需求方未提供明确的参数逻辑，且没有显式声明这是一个"空参数命令"，**必须立即终止当前技能执行**，向主代理/用户抛出错误："缺少 Command 参数定义。请提供相关的参数逻辑及类型信息，或明确确认该命令无参数。"

# 文件路径规范 (File Routing)
生成的文件必须放置于对应的上下文中：
`/<context_name>/application/commands/<command_name_in_snake_case>.py`

# 核心代码模板 (Code Template)
请严格遵循以下现代 Python 推荐写法生成代码（使用类型注解和 `dataclasses`）。将 `<Placeholder>` 替换为实际上下文：

```python
from dataclasses import dataclass

# 替换为实际的 UnitOfWork 端口路径和基础 Command 类路径
from <context_name>.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.command import Command
# 引入该命令所需的值对象或领域类型
from <module_path>.domain.value_objects import <DomainValueObject>


class <ActionName>Command(Command):
    """
    <ActionName> 命令
    """
    # 以下属性由传入的参数逻辑生成
    # 注意：若是空参数命令，此处写 pass
    <field_name>: <DomainValueObject>


@dataclass
class <ActionName>CommandHandler:
    """
    <ActionName> 命令处理器代码桩
    """

    def execute(self, cmd: <ActionName>Command, uow: UnitOfWork) -> None:
        """
        执行具体的命令逻辑。
        当前为脚手架阶段，不实现具体业务逻辑。
        """
        ...
```

# 快速参考

## 命名规范
- **Command 类名**：`<Verb><Noun>Command` 格式
  - 示例：`RemoveModuleCommand`, `CreateUserCommand`, `UpdateOrderStatusCommand`
- **CommandHandler 类名**：`<Verb><Noun>CommandHandler` 格式
  - 示例：`RemoveModuleCommandHandler`, `CreateUserCommandHandler`
- **文件名**：`<verb>_<noun>.py` 格式（snake_case）
  - 示例：`remove_module.py`, `create_user.py`

## 参数类型映射示例

| 业务含义 | 值对象类型 | Python 类型 |
|---------|-----------|-------------|
| 模块 ID | `ModuleId` | `str` 或 `UUID` |
| 用户名 | `UserName` | `str` |
| 金额 | `Money` | `Decimal` |
| 日期 | `Date` | `datetime` |

## 完整示例

**输入参数**：
```json
{
  "context_name": "architecture",
  "command_name": "RemoveModule",
  "parameters": {
    "module_id": "ModuleId"
  }
}
```

**生成的文件路径**：
`/architecture/application/commands/remove_module.py`

**生成的代码**：
```python
from dataclasses import dataclass

from architecture.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.command import Command
from architecture.domain.value_objects import ModuleId


class RemoveModuleCommand(Command):
    """
    RemoveModule 命令
    """
    module_id: ModuleId


@dataclass
class RemoveModuleCommandHandler:
    """
    RemoveModule 命令处理器代码桩
    """

    def execute(self, cmd: RemoveModuleCommand, uow: UnitOfWork) -> None:
        """
        执行具体的命令逻辑。
        当前为脚手架阶段，不实现具体业务逻辑。
        """
        ...
```
