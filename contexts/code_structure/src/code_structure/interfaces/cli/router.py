import typer

from code_structure.interfaces.cli.move_class import move_class

code_structure_app = typer.Typer(
    name="structure", help="Code Structure Context Commands (代码结构上下文指令)"
)

code_structure_app.command("move-class")(move_class)
