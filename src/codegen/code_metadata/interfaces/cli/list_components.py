import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.application.queries.list_components import ListComponents
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery

console = Console()


@inject
def _list_components(
    query: PageQuery[ComponentFilter],
    use_case: ListComponents = Provide["code_metadata_container.list_components"],
) -> Page[ComponentDto]:
    return use_case.execute(query)


def list_components(
    type: Annotated[
        str | None, typer.Option("--type", "-t", help="Filter by component type")
    ] = None,
    context: Annotated[
        str | None, typer.Option("--context", "-c", help="Filter by context name")
    ] = None,
    name: Annotated[
        str | None, typer.Option("--name", "-n", help="Filter by component name")
    ] = None,
    page: Annotated[int, typer.Option("--page", "-p", help="Page number")] = 1,
    size: Annotated[int, typer.Option("--size", "-s", help="Page size")] = 10,
) -> None:
    """List components with optional filters and pagination."""
    query = PageQuery(
        current=page,
        size=size,
        condition=ComponentFilter(type=type, context=context, name=name),
    )
    result = _list_components(query)
    for item in result.items:
        console.print(
            f"[bold]{item.name}-{item.id}[/bold] ({item.type}) - {item.context}"
        )
        console.print(f"  {item.description}")
    console.print(
        f"\nPage {result.current} / {(-(-result.total // result.size) if result.size else 0)} (total: {result.total})"
    )
