from typing import Annotated
import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from rich.table import Table
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.application.queries.find_unused_nodes import FindUnusedNodes
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind

console = Console()
SUPPORTED_KINDS: set[CodeNodeKind] = {
    CodeNodeKind.MODULE,
    CodeNodeKind.METHOD,
    CodeNodeKind.CLASS,
    CodeNodeKind.FUNCTION,
    CodeNodeKind.VARIABLE,
}


@inject
def _find_unused_nodes(
    kind: CodeNodeKind,
    use_case: FindUnusedNodes = Provide["code_metadata_container.find_unused_nodes"],
) -> list[CodeNode]:
    return use_case.execute(kind)


def list_unused_nodes(
    type: Annotated[
        CodeNodeKind,
        typer.Argument(
            help="CodeNode kind to filter (supported: class, function, variable)"
        ),
    ],
) -> None:
    """List unused CodeNodes of a given kind."""
    if type not in SUPPORTED_KINDS:
        console.print(
            f"[red]Error: kind '{type}' is not supported yet. Supported: {', '.join((k.value.lower() for k in sorted(SUPPORTED_KINDS)))}[/red]"
        )
        raise typer.Exit(1)
    try:
        nodes = _find_unused_nodes(type)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    if not nodes:
        console.print(f"[green]No unused {type.value.lower()} nodes found.[/green]")
        return
    table = Table(title=f"Unused {type.value.capitalize()} Nodes", show_lines=True)
    table.add_column("#", style="dim", justify="right")
    table.add_column("FQN", style="green")
    table.add_column("Name", style="cyan")
    for idx, node in enumerate(nodes, 1):
        table.add_row(str(idx), node.id, node.name)
    console.print(table)
    console.print(
        f"\n[dim]Total: {len(nodes)} unused {type.value.lower()} node(s)[/dim]"
    )
