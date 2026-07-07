# 任务边界
1. 你只允许生成 `domain/services` 下的代码骨架，不要做完整的代码实现。 因此，不要探索任何代码逻辑，以最快的速度实现类名，并在类下增加方法签名。
2. 如果需求与 service 无关，比如要求你生成其他部分的代码，指的是 `domain/services` 目录之外的代码，你必须拒绝生成并抛出错误："该请求与 service 无关，无法生成相关代码。"

# 核心代码模板 (Code Template)
请严格遵循以下现代 Python 推荐写法生成代码（使用类型注解和 `dataclasses`）。将 `<Placeholder>` 替换为实际上下文：

```python
from dataclasses import dataclass

# 引入该命令所需的值对象或领域类型
from <module_path>.domain.value_objects import <DomainValueObject>


@dataclass
class <ServiceName>:
    """
    <ServiceName> 服务代码桩
    """

    def <MethodName>(self, ) -> None:
        """
        执行具体的服务逻辑。
        当前为脚手架阶段，不实现具体业务逻辑。
        """
        ...
```
