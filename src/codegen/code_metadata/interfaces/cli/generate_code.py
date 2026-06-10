import typer
from typing import Annotated
from rich.console import Console
from rich.syntax import Syntax
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.code_metadata.application.commands.generate_code import GenerateCode
from codegen.code_metadata.application.dtos.generate_code_command import (
    GenerateCodeCommand,
)
from codegen.code_metadata.application.dtos.generate_code_result import (
    GenerateCodeResult,
)

console = Console()


@inject
def _generate_code(
    cmd: GenerateCodeCommand,
    use_case: GenerateCode = Provide["code_metadata_container.generate_code"],
) -> GenerateCodeResult:
    return use_case.execute(cmd)


def generate_code(fqn: Annotated[str, typer.Argument()]) -> None:
    """Generate Python code from a stored component."""
    cmd = GenerateCodeCommand(fqn=fqn)
    result = _generate_code(cmd)
    console.print(Syntax(result.code, "python"))
