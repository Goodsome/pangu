import logging
from dataclasses import dataclass
from pathlib import Path

from architecture.domain.services.fqn_service import FqnService
from foundation.building_blocks.command import Command
from foundation.system.context_registry import ContextRegistry
from foundation.common_types.fqns.fqn import ModuleFqn

from code_structure.application.ports.unit_of_work import UnitOfWork
from code_structure.domain.ports.symbol_scanner import SymbolScanner
from code_structure.domain.serivces.sync_module_symbols_service import (
    SyncModuleSymbolsService,
)
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule

logger = logging.getLogger(__name__)


class SyncStagedModuleSymbolsCommand(Command):
    """
    SyncStagedModuleSymbolsCommand 命令，用于增量同步 staged 模块的 symbols 和边
    """

    file_path: list[Path]


@dataclass
class SyncStagedModuleSymbolsCommandHandler:
    """
    SyncStagedModuleSymbolsCommand 的命令处理器，只承担用例编排职责
    """

    symbol_scanner: SymbolScanner
    sync_service: SyncModuleSymbolsService

    def execute(self, cmd: SyncStagedModuleSymbolsCommand, uow: UnitOfWork) -> None:
        # 1. 过滤并转换 staged 文件的路径到 module_fqns
        module_fqns = [
            FqnService.build_module_fqn(path)
            for path in cmd.file_path
            if path.suffix == ".py"
            and path.stem != "__init__"
            and ContextRegistry.check_path_in_contexts(path)
        ]
        if not module_fqns:
            logger.info("No staged Python modules to sync.")
            return

        # 2. 扫描这些模块的代码文件，生成 parsed_file_modules
        parsed_file_modules = self.symbol_scanner.scan(module_fqns)
        parsed_modules_by_fqn = {pfm.fqn: pfm for pfm in parsed_file_modules}

        # 3. 对每个扫描出的模块分发执行增量同步
        for module_fqn in module_fqns:
            parsed_file_module = parsed_modules_by_fqn.get(module_fqn)
            if parsed_file_module and parsed_file_module.exists:
                self._sync_single_module(module_fqn, parsed_file_module, uow)

    def _sync_single_module(
        self,
        module_fqn: ModuleFqn,
        parsed_file_module: ParsedFileModule,
        uow: UnitOfWork,
    ) -> None:
        """对单个模块及其关联的 Symbol 聚合执行增量比对、同步与持久化编排"""
        # 直接获取已有的 file_module
        file_module = uow.file_modules.get_by_fqn(module_fqn)

        # 通过 FQN 前缀批量查询已存在的 Symbol 聚合根
        fqn_prefix = f"{module_fqn}::"
        existing_classes = uow.classes.find_by_fqn_prefix(fqn_prefix)
        existing_functions = uow.functions.find_by_fqn_prefix(fqn_prefix)
        existing_variables = uow.variables.find_by_fqn_prefix(fqn_prefix)

        # 预查外部导入，用作查重
        existing_external_fqns = self._get_existing_external_fqns(
            parsed_file_module, uow
        )

        # 调用领域服务进行增量比对和同步，得到变更清单
        sync_result = self.sync_service.sync(
            file_module=file_module,
            parsed_file_module=parsed_file_module,
            existing_classes=existing_classes,
            existing_functions=existing_functions,
            existing_variables=existing_variables,
            existing_external_fqns=existing_external_fqns,
        )

        # 保存与提交变更
        for cls in sync_result.saved_classes:
            uow.classes.save(cls)
        for cls in sync_result.deleted_classes:
            uow.classes.delete(cls)

        for func in sync_result.saved_functions:
            uow.functions.save(func)
        for func in sync_result.deleted_functions:
            uow.functions.delete(func)

        for var in sync_result.saved_variables:
            uow.variables.save(var)
        for var in sync_result.deleted_variables:
            uow.variables.delete(var)

        for ext in sync_result.new_external_symbols:
            uow.external_symbols.add(ext)

        uow.file_modules.save(file_module)

    def _get_existing_external_fqns(
        self, parsed_file_module: ParsedFileModule, uow: UnitOfWork
    ) -> set[str]:
        fqns: set[str] = set()
        for imp in parsed_file_module.imports:
            is_internal = ContextRegistry.check_is_internal(imp.target_fqn.context)
            if not is_internal:
                try:
                    ext = uow.external_symbols.get_by_fqn(imp.target_fqn)
                    fqns.add(str(ext.fqn))
                except ValueError:
                    pass
        return fqns
