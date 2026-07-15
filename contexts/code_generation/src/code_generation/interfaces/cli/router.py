import typer

from code_generation.interfaces.cli.generate_aggregate import generate_aggregate

generation_app = typer.Typer(
    name="generation", help="Code Generation Context Commands (代码生成上下文指令)"
)
generation_app.command("generate-aggregate")(generate_aggregate)
