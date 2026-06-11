from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from codegen.code_metadata.application.commands.sync_module import (
    SyncModuleCommand,
    SyncModuleHandler,
)

console = Console()


@inject
def _sync_module(
    cmd: SyncModuleCommand,
    handler: SyncModuleHandler = Provide["code_metadata_container.sync_module"],
) -> None:
    handler.execute(cmd)


def sync_module(
    module_fqn: Annotated[
        str, typer.Argument(help="The FQN of the module to sync")
    ],
) -> None:
    """Sync a module: regenerate code or delete empty modules."""
    cmd = SyncModuleCommand(module_fqn=module_fqn)
    try:
        _sync_module(cmd)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Module '{module_fqn}' synced successfully.[/green]")
