from typing import Annotated
import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from rich.tree import Tree
from codegen.code_metadata.application.dtos.node_tree import NodeTree
from codegen.code_metadata.application.queries.get_directory_tree import (
    GetDirectoryTree,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind

console = Console()
ICONS = {CodeNodeKind.DIRECTORY: "📁", CodeNodeKind.FILE: "📄"}


@inject
def _get_directory_tree(
    fqn_prefix: str,
    use_case: GetDirectoryTree = Provide["code_metadata_container.get_directory_tree"],
) -> NodeTree:
    return use_case.execute(fqn_prefix)


def _add_children(parent: Tree, node_tree: NodeTree) -> None:
    for child in node_tree.children:
        icon = ICONS.get(child.node.kind, "📄")
        branch = parent.add(
            f"{icon} [bold]{child.node.name}[/bold]  [dim]{child.node.fqn}[/dim]"
        )
        _add_children(branch, child)


def get_directory_tree(
    fqn_prefix: Annotated[
        str, typer.Argument(help="FQN prefix of the root directory node")
    ],
) -> None:
    """Display a code-node directory tree rooted at the given FQN prefix."""
    try:
        root = _get_directory_tree(fqn_prefix)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    icon = ICONS.get(root.node.kind, "📄")
    tree = Tree(f"{icon} [bold]{root.node.name}[/bold]  [dim]{root.node.fqn}[/dim]")
    _add_children(tree, root)
    console.print(tree)
