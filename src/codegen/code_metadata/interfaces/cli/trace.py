from typing import Annotated
import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from rich.tree import Tree
from codegen.code_metadata.application.dtos.graph_view import GraphViewNode
from codegen.code_metadata.application.dtos.trace_query import (
    TraceSymbolDependenciesQuery,
)
from codegen.code_metadata.application.queries.trace_symbol_dependencies import (
    TraceSymbolDependenciesQueryHandler,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection

console = Console()
KIND_ICONS = {
    CodeNodeKind.DIRECTORY: "📁",
    CodeNodeKind.FILE: "📄",
    CodeNodeKind.MODULE: "📦",
    CodeNodeKind.CLASS: "🏢",
    CodeNodeKind.FUNCTION: "⚡",
    CodeNodeKind.METHOD: "⚡",
    CodeNodeKind.VARIABLE: "🔶",
    CodeNodeKind.EXTERNAL: "🔌",
}
EDGE_LABELS = {
    EdgeType.CONTAINS: "CONTAINS",
    EdgeType.DEFINES: "DEFINES",
    EdgeType.DEFINES_MODULE: "DEFINES_MODULE",
    EdgeType.IMPORTS: "IMPORTS",
    EdgeType.CALLS: "CALLS",
    EdgeType.INHERITS: "INHERITS",
    EdgeType.EXPORTS: "EXPORTS",
    EdgeType.IMPLEMENTS: "IMPLEMENTS",
    EdgeType.TYPED_AS: "TYPED_AS",
    EdgeType.RETURNS: "RETURNS",
    EdgeType.ACCEPTS: "ACCEPTS",
}


@inject
def _trace_symbol_dependencies(
    query: TraceSymbolDependenciesQuery,
    handler: TraceSymbolDependenciesQueryHandler = Provide[
        "code_metadata_container.trace_symbol_dependencies"
    ],
) -> GraphViewNode:
    result = handler.execute(query)
    return result.root


def _node_label(node) -> str:
    icon = KIND_ICONS.get(node.kind, "❓")
    return f"{icon} {node.kind.value.capitalize()}: {node.fqn}"


def _render_node(parent: Tree, gv_node: GraphViewNode, is_last: bool) -> None:
    if gv_node.node is None:
        edge_label = (
            EDGE_LABELS.get(gv_node.edge_type, str(gv_node.edge_type))
            if gv_node.edge_type is not None
            else "UNKNOWN"
        )
        section = parent.add(f"⚡ {edge_label}:", guide_style="bold cyan")
        _render_children(section, gv_node.children)
        return
    label = _node_label(gv_node.node)
    if gv_node.edge_type is not None:
        edge_label = EDGE_LABELS.get(gv_node.edge_type, str(gv_node.edge_type))
        label = f"➔ [{edge_label}] {label}"
    branch = parent.add(label, guide_style="bold green" if is_last else "dim")
    _render_children(branch, gv_node.children)


def _render_children(parent: Tree, children: list[GraphViewNode]) -> None:
    for i, child in enumerate(children):
        _render_node(parent, child, is_last=i == len(children) - 1)


def trace(
    fqn: Annotated[
        str, typer.Argument(help="Fully qualified name of the target symbol")
    ],
    direction: Annotated[
        EdgeDirection, typer.Option("--direction", "-d", help="Trace direction")
    ] = EdgeDirection.OUT,
    edge_type: Annotated[
        EdgeType | None, typer.Option("--edge-type", "-e", help="Filter by edge type")
    ] = None,
    depth: Annotated[
        int, typer.Option("--depth", help="Maximum trace depth (1-5)")
    ] = 1,
) -> None:
    """Trace symbol dependencies in the code graph."""
    if not 1 <= depth <= 5:
        console.print("[red]Error: --depth must be between 1 and 5[/red]")
        raise typer.Exit(1)
    query = TraceSymbolDependenciesQuery(
        target_fqn=fqn, direction=direction, edge_type=edge_type, depth=depth
    )
    try:
        root = _trace_symbol_dependencies(query)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    if root.node is None:
        console.print("[yellow]No dependencies found.[/yellow]")
        return
    tree = Tree(_node_label(root.node))
    _render_children(tree, root.children)
    console.print(tree)
