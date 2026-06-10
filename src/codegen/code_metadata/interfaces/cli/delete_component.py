import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.code_metadata.application.commands.delete_component import DeleteComponent
from codegen.code_metadata.application.dtos.delete_component_command import (
    DeleteComponentCommand,
)

console = Console()


@inject
def _delete_component(
    cmd: DeleteComponentCommand,
    use_case: DeleteComponent = Provide["code_metadata_container.delete_component"],
) -> None:
    use_case.execute(cmd)


def delete_component(
    component_id: Annotated[
        str, typer.Argument(help="The UUID of the component to delete")
    ],
) -> None:
    """Delete a stored component by its ID."""
    cmd = DeleteComponentCommand(component_id=component_id)
    _delete_component(cmd)
    console.print(f"[green]Component {component_id} deleted successfully.[/green]")
