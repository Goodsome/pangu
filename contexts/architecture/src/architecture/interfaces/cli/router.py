import typer

from architecture.interfaces.cli.init_project_graph import init_project_graph

arch_app = typer.Typer(
    name="arch", 
    help="Architecture Context Commands (架构上下文指令)"
)

arch_app.command("init-graph")(init_project_graph)
