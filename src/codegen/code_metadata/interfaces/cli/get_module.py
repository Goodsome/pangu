import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.code_metadata.application.services.project_sync_service import (
    ProjectSyncService,
)

console = Console()


@inject
def _get_module(
    path: str,
    service: ProjectSyncService = Provide[
        "code_metadata_container.project_sync_service"
    ],
) -> None:
    module = service.get_module(path=path)
    if module:
        console.print(module)


def get_module(path: Annotated[str, typer.Argument()]) -> None:
    """Get module."""
    _get_module(path)
