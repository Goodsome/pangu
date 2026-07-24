import asyncio
from pathlib import Path
from typing import Annotated
from architecture.interfaces.cli.init_project_graph import init_project_graph
from architecture.interfaces.cli.sync_staged_modules import sync_staged_modules
from code_structure.interfaces.cli.init_symbol_graph import init_symbol_graph
from code_structure.interfaces.cli.sync_staged_module_symbols import (
    sync_staged_module_symbols,
)
import typer
from foundation.logging_setup import configure_logging
from pangu_cli.container import create_container
from pangu_cli.run_outbox_worker import run_worker
from architecture.interfaces.cli import arch_app
from code_dom.interfaces.cli import code_dom_app
from code_generation.interfaces.cli import generation_app
from code_structure.interfaces.cli import code_structure_app
from d4_automation.interfaces.cli.router import d4_automation_app


app = typer.Typer(
    name="pangu",
    help="Pangu CLI - DDD Project Scaffolding Tool.",
    add_completion=False,
    rich_markup_mode="markdown",
)
app.add_typer(arch_app, name="arch")
app.add_typer(code_dom_app, name="dom")
app.add_typer(generation_app, name="generation")
app.add_typer(code_structure_app, name="structure")
app.add_typer(d4_automation_app, name="d4-automation")

app.command()(run_worker)

@app.command(name="init-graph")
def init_graph() -> None:
    init_project_graph()
    init_symbol_graph()


@app.command(name="sync-stg")
def sync_stg(
    files: Annotated[
        list[Path] | None, typer.Argument(help="需要同步的文件列表（支持传入多个文件）")
    ],
) -> None:
    """增量同步已 staged 的代码文件中的 symbols 节点和相关依赖边"""
    if not files:
        raise typer.Exit()
    sync_staged_modules(files)
    sync_staged_module_symbols(files)


def main():
    """Bootstrap the DI container and run the CLI app."""
    configure_logging(
        app_name="cli",
        log_dir=Path.cwd() / "logs",
        console_output=False,
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
            "code_generation.interfaces.cli",
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
