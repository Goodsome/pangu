import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.code_metadata.application.commands.generate_code import GenerateCodeCommand
from codegen.code_metadata.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _generate_code(
    cmd: GenerateCodeCommand,
    message_bus: MessageBus = Provide["code_metadata_container.message_bus"],
) -> None:
    message_bus.handle(cmd)


def generate_code(fqn: Annotated[str, typer.Argument()]) -> None:
    """Generate Python code from a stored component."""
    cmd = GenerateCodeCommand(fqns=[fqn])
    _generate_code(cmd)
