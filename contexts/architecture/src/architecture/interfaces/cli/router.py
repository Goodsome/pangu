import typer

from architecture.interfaces.cli.create_package import create_package
from architecture.interfaces.cli.init_project_graph import init_project_graph
from architecture.interfaces.cli.listen import listen
from architecture.interfaces.cli.move_module import move_module
from architecture.interfaces.cli.remove_module import remove_module
from architecture.interfaces.cli.sync_staged_modules import sync_staged_modules

arch_app = typer.Typer(
    name="arch",
    help="Architecture Context Commands (架构上下文指令)"
)

arch_app.command("create-package")(create_package)
arch_app.command("init-graph")(init_project_graph)
arch_app.command("listen")(listen)
arch_app.command("move-module")(move_module)
arch_app.command("remove-module")(remove_module)
arch_app.command("sync-stg")(sync_staged_modules)
