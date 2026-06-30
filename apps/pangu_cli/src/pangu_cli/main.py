import asyncio
from pathlib import Path
from code_structure.interfaces.cli.init_symbol_graph import init_symbol_graph
import typer
from foundation.logging_setup import configure_logging
from pangu_cli.container import create_container
from pangu_cli.run_outbox_worker import run_worker
from architecture.interfaces.cli import arch_app
from code_dom.interfaces.cli import code_dom_app

app = typer.Typer(
    name="pangu",
    help="Pangu CLI - DDD Project Scaffolding Tool.",
    add_completion=False,
    rich_markup_mode="markdown",
)
app.add_typer(arch_app, name="arch")
app.add_typer(code_dom_app, name="dom")
app.command()(run_worker)

@app.command(name="init-graph")
def init_graph() -> None:
    # init_project_graph()
    init_symbol_graph()
    

def main():
    """Bootstrap the DI container and run the CLI app."""
    configure_logging(
        app_name="cli",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    container = loop.run_until_complete(create_container())
    container.wire(
        packages=[
            "architecture.interfaces.cli",
            "code_structure.interfaces.cli",
            "code_dom.interfaces.cli",
            "pangu_cli",
        ]
    )
    try:
        app()
    finally:
        shutdown_resources = container.shutdown_resources()
        if shutdown_resources:
            loop.run_until_complete(shutdown_resources)
        loop.close()


if __name__ == "__main__":
    main()
