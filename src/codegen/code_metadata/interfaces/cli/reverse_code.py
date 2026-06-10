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
def _reverse_code(
    context: str,
    component_type: str | None,
    component_name: str | None,
    service: ProjectSyncService = Provide[
        "code_metadata_container.project_sync_service"
    ],
) -> None:
    service.reverse_code(
        context=context, component_type=component_type, component_name=component_name
    )


def reverse_code(
    context: Annotated[str, typer.Argument()],
    component_type: Annotated[str | None, typer.Option("--type", "-t")] = None,
    component_name: Annotated[str | None, typer.Option("--name", "-n")] = None,
) -> None:
    """Reverse code."""
    _reverse_code(context, component_type, component_name)
