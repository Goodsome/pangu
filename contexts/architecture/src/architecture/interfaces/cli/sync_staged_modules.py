from pathlib import Path
from typing import Annotated
from dependency_injector.wiring import Provide, inject
from typer import Argument, Exit
from architecture.application.commands.sync_staged_modules import SyncStagedModulesCommand
from foundation.message_bus.message_bus import BaseMessageBus


@inject
def _sync_staged_modules(
    cmd: SyncStagedModulesCommand,
    message_bus: BaseMessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def sync_staged_modules(
    files: Annotated[list[Path] | None, Argument(
        help="需要同步的文件列表（支持传入多个文件）"
    )]
) -> None:
    if not files:
        raise Exit()
    cmd = SyncStagedModulesCommand(file_path=files)
    _sync_staged_modules(cmd)
