from pathlib import Path
from typing import Annotated
from dependency_injector.wiring import Provide, inject
from typer import Argument, Exit

from code_structure.application.commands.sync_staged_module_symbols import (
    SyncStagedModuleSymbolsCommand,
)
from foundation.message_bus.message_bus import BaseMessageBus


@inject
def _sync_staged_module_symbols(
    cmd: SyncStagedModuleSymbolsCommand,
    message_bus: BaseMessageBus = Provide["code_structure_container.message_bus"],
) -> None:
    message_bus.handle(cmd)


def sync_staged_module_symbols(
    files: Annotated[
        list[Path] | None, Argument(help="需要增量更新的符号文件列表（支持传入多个文件）")
    ] = None,
) -> None:
    """增量同步已 staged 的代码文件中的 symbols 节点和相关依赖边"""
    if not files:
        raise Exit()
    
    # 过滤出 python 文件
    files = [file for file in files if file.suffix == ".py"]
    if not files:
        return

    cmd = SyncStagedModuleSymbolsCommand(file_path=files)
    _sync_staged_module_symbols(cmd)
