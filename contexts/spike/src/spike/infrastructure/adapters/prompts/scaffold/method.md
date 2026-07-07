# 触发条件与参数校验 (Validation Rules)
在执行代码生成前，必须从主任务/需求方获取以下信息，如果信息不足，返回报错。
1. **上下文 (Bounded Context)**：命令所属的模块名称（用于确定文件路径）。
2. **类名称 (Class Name)**：所属类名称，如果发现重名的类名，需要确认文件路径。
3. **方法名称 (Method Name)**：方法名称
4. **参数逻辑 (Parameters)**：方法的参数签名，需要明确入参和返回类型。
   
# 任务边界
1. 你只允许生成方法的代码骨架，不要做完整的代码实现。因此，不要探索任何代码逻辑，以最快的速度定位类名，并在类下增加方法签名。

# 示例

`undefine_class` 为本次新增加方法，用 `...` 占位符表示方法体为空。

```python

class FileModule(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str

    _classes: set[ClassId] = PrivateAttr(default_factory=set)
    _functions: set[FunctionId] = PrivateAttr(default_factory=set)
    _variables: set[VariableId] = PrivateAttr(default_factory=set)

    def define_class(self, class_id: ClassId) -> None:
        self._classes.add(class_id)
        self.add_mutation(AddModuleDefinesEdge(source_id=self.id, target_id=class_id))

    def undefine_class(self, class_id: ClassId) -> None:
        """Remove class definition from module."""
        ...

```