from dataclasses import dataclass, field

from foundation.common_types.fqns.fqn import ClassFqn, FunctionFqn, VariableFqn
from foundation.system.context_registry import ContextRegistry
from code_structure.domain.identities.symbol_ids import (
    ClassId,
    FunctionId,
    VariableId,
    ExternalSymbolId,
)
from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.aggregates.external_symbol import ExternalSymbol
from code_structure.domain.aggregates.file_module import FileModule
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule
from code_structure.domain.serivces.class_symbol_registry import ClassRegistry
from code_structure.domain.serivces.function_symbol_registry import FunctionRegistry
from code_structure.domain.serivces.variable_symbol_registry import VariableRegistry


@dataclass
class SyncResult:
    """
    增量同步的结果清单，包含需要保存与删除的领域实体
    """

    saved_classes: list[ClassSymbol] = field(default_factory=list)
    deleted_classes: list[ClassSymbol] = field(default_factory=list)
    saved_functions: list[FunctionSymbol] = field(default_factory=list)
    deleted_functions: list[FunctionSymbol] = field(default_factory=list)
    saved_variables: list[VariableSymbol] = field(default_factory=list)
    deleted_variables: list[VariableSymbol] = field(default_factory=list)
    new_external_symbols: list[ExternalSymbol] = field(default_factory=list)


class SyncModuleSymbolsService:
    """
    SyncModuleSymbolsService 领域服务，负责跨聚合的增量同步和防重逻辑
    """

    def sync(
        self,
        file_module: FileModule,
        parsed_file_module: ParsedFileModule,
        existing_classes: list[ClassSymbol],
        existing_functions: list[FunctionSymbol],
        existing_variables: list[VariableSymbol],
        existing_external_fqns: set[str],
    ) -> SyncResult:
        result = SyncResult()

        # 初始化内存注册表作为映射
        class_registry = ClassRegistry.init(existing_classes)
        function_registry = FunctionRegistry.init(existing_functions)
        variable_registry = VariableRegistry.init(existing_variables)

        # 1. 增量同步子符号聚合本身的状态，不直接触碰 file_module
        self._sync_classes(parsed_file_module, class_registry, existing_classes, result)
        self._sync_functions(
            parsed_file_module, function_registry, existing_functions, result
        )
        self._sync_variables(
            parsed_file_module, variable_registry, existing_variables, result
        )

        # 2. 检测并生成缺失的外部依赖符号
        self._sync_imports(parsed_file_module, existing_external_fqns, result)

        # 3. 作为独立职责，在此方法中更新 file_module 的子符号绑定及导入列表
        self._sync_file_module(file_module, parsed_file_module, result)

        return result

    def _sync_classes(
        self,
        parsed_file_module: ParsedFileModule,
        class_registry: ClassRegistry,
        existing_classes: list[ClassSymbol],
        result: SyncResult,
    ) -> None:
        parsed_classes_fqns: set[ClassFqn] = set()
        for parsed_class in parsed_file_module.classes:
            class_fqn = ClassFqn(f"{parsed_file_module.fqn}::{parsed_class.name}")
            parsed_classes_fqns.add(class_fqn)

            if class_registry.contains_fqn(class_fqn):
                # 依然存在，复用并同步更新内部状态
                class_symbol = class_registry._store_by_fqn[class_fqn]
                class_symbol.sync_from_parsed_class(parsed_class)
                result.saved_classes.append(class_symbol)
            else:
                # 新增
                class_symbol = ClassSymbol(
                    id=ClassId.create(),
                    name=parsed_class.name,
                    fqn=class_fqn,
                )
                class_symbol.sync_from_parsed_class(parsed_class)
                class_registry.register(class_symbol)
                result.saved_classes.append(class_symbol)

        # 收集不再存在的类
        for class_symbol in existing_classes:
            if class_symbol.fqn not in parsed_classes_fqns:
                result.deleted_classes.append(class_symbol)

    def _sync_functions(
        self,
        parsed_file_module: ParsedFileModule,
        function_registry: FunctionRegistry,
        existing_functions: list[FunctionSymbol],
        result: SyncResult,
    ) -> None:
        parsed_funcs_fqns: set[FunctionFqn] = set()
        for parsed_func in parsed_file_module.functions:
            func_fqn = FunctionFqn(f"{parsed_file_module.fqn}::{parsed_func.name}")
            parsed_funcs_fqns.add(func_fqn)

            if function_registry.contains_fqn(func_fqn):
                func_symbol = function_registry._store_by_fqn[func_fqn]
                func_symbol.sync_from_parsed_function(parsed_func)
                result.saved_functions.append(func_symbol)
            else:
                func_symbol = FunctionSymbol(
                    id=FunctionId.create(),
                    name=parsed_func.name,
                    fqn=func_fqn,
                )
                func_symbol.sync_from_parsed_function(parsed_func)
                function_registry.register(func_symbol)
                result.saved_functions.append(func_symbol)

        # 收集不再存在的函数
        for func_symbol in existing_functions:
            if func_symbol.fqn not in parsed_funcs_fqns:
                result.deleted_functions.append(func_symbol)

    def _sync_variables(
        self,
        parsed_file_module: ParsedFileModule,
        variable_registry: VariableRegistry,
        existing_variables: list[VariableSymbol],
        result: SyncResult,
    ) -> None:
        parsed_vars_fqns: set[VariableFqn] = set()
        for parsed_var in parsed_file_module.variables:
            var_fqn = VariableFqn(f"{parsed_file_module.fqn}::{parsed_var.name}")
            parsed_vars_fqns.add(var_fqn)

            if variable_registry.contains_fqn(var_fqn):
                var_symbol = variable_registry._store_by_fqn[var_fqn]
                var_symbol.sync_from_parsed_variable(parsed_var)
                result.saved_variables.append(var_symbol)
            else:
                var_symbol = VariableSymbol(
                    id=VariableId.create(),
                    name=parsed_var.name,
                    fqn=var_fqn,
                )
                var_symbol.sync_from_parsed_variable(parsed_var)
                variable_registry.register(var_symbol)
                result.saved_variables.append(var_symbol)

        # 收集不再存在的变量
        for var_symbol in existing_variables:
            if var_symbol.fqn not in parsed_vars_fqns:
                result.deleted_variables.append(var_symbol)

    def _sync_imports(
        self,
        parsed_file_module: ParsedFileModule,
        existing_external_fqns: set[str],
        result: SyncResult,
    ) -> None:
        """检测并生成缺失的外部依赖符号"""
        for parsed_import in parsed_file_module.imports:
            is_internal = ContextRegistry.check_is_internal(parsed_import.target_fqn.context)
            if not is_internal:
                if str(parsed_import.target_fqn) not in existing_external_fqns:
                    ext_symbol = ExternalSymbol(
                        id=ExternalSymbolId.create(),
                        name=parsed_import.target_fqn.symbol,
                        fqn=parsed_import.target_fqn,
                    )
                    result.new_external_symbols.append(ext_symbol)
                    existing_external_fqns.add(str(parsed_import.target_fqn))

    def _sync_file_module(
        self,
        file_module: FileModule,
        parsed_file_module: ParsedFileModule,
        result: SyncResult,
    ) -> None:
        """独立方法：负责更新 file_module 的子符号绑定关系与 imports"""
        # 1) 解绑已经删除的旧符号
        for cls in result.deleted_classes:
            file_module.undefine_class(cls.id)
        for func in result.deleted_functions:
            file_module.undefine_function(func.id)
        for var in result.deleted_variables:
            file_module.undefine_variable(var.id)

        # 2) 绑定新定义及复用的符号
        for cls in result.saved_classes:
            file_module.define_class(cls.id)
        for func in result.saved_functions:
            file_module.define_function(func.id)
        for var in result.saved_variables:
            file_module.define_variable(var.id)

        # 3) 设置最新的 imports
        file_module.set_imports(parsed_file_module.imports)
