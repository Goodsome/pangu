import asyncio
from pathlib import Path
import typer
from foundation.logging_setup import configure_logging
from pangu_cli.container import create_container
from codegen.code_metadata.interfaces.cli.clean_node import clean_node
from codegen.code_metadata.interfaces.cli.generate_code import generate_code
from codegen.code_metadata.interfaces.cli.get_code_node import get_code_node
from codegen.code_metadata.interfaces.cli.get_dev_progress import get_dev_progress
from codegen.code_metadata.interfaces.cli.ingest_project import ingest_project
from codegen.code_metadata.interfaces.cli.list_unused_nodes import list_unused_nodes
from codegen.code_metadata.interfaces.cli.listen import listen
from codegen.code_metadata.interfaces.cli.move_node import move_node, move_to_ast_stmt
from codegen.code_metadata.interfaces.cli.rename_node import rename_node
from pangu_cli.run_outbox_worker import run_worker
from architecture.interfaces.cli import arch_app
from codegen.code_dom.interfaces.cli import code_dom_app

app = typer.Typer(
    name="pangu",
    help="Pangu CLI - DDD Project Scaffolding Tool.",
    add_completion=False,
    rich_markup_mode="markdown",
)
app.add_typer(arch_app, name="arch")
app.add_typer(code_dom_app, name="dom")
app.command()(generate_code)
app.command()(get_dev_progress)
app.command()(clean_node)
app.command()(ingest_project)
app.command()(get_code_node)
app.command()(list_unused_nodes)
app.command()(run_worker)
app.command()(listen)
app.command()(move_node)
app.command()(move_to_ast_stmt)
app.command()(rename_node)


def main():
    """Bootstrap the DI container and run the CLI app."""
    # setup_cli_logging()
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
            "codegen.code_metadata.interfaces.cli",
            "codegen.code_dom.interfaces.cli",
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
