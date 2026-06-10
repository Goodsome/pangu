import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.code_metadata.application.services.project_sync_service import (
    ProjectSyncService,
)
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.shared.application.dtos.page import Page

console = Console()


@inject
def _list_modules(
    current: int,
    size: int,
    service: ProjectSyncService = Provide[
        "code_metadata_container.project_sync_service"
    ],
) -> Page[Module]:
    return service.list_modules()


def list_modules(
    page: Annotated[int, typer.Option("--page", "-p", help="Page number")] = 1,
    size: Annotated[int, typer.Option("--size", "-s", help="Page size")] = 10,
) -> None:
    """List components with optional filters and pagination."""
    result = _list_modules(current=page, size=size)
    for item in result.items:
        console.print(f"[bold]{item.name}-{item.id}[/bold] ({item.path})")
    console.print(
        f"\nPage {result.current} / {(-(-result.total // result.size) if result.size else 0)} (total: {result.total})"
    )
