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
def _get_component(
    context: str,
    component_name: str,
    service: ProjectSyncService = Provide[
        "code_metadata_container.project_sync_service"
    ],
) -> None:
    component = service.get_component(context=context, component_name=component_name)
    if component:
        console.print(component)


def get_component(
    context: Annotated[str, typer.Argument()],
    component_name: Annotated[str, typer.Argument()],
) -> None:
    """Get component."""
    _get_component(context, component_name)
