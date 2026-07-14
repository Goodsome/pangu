import subprocess
from pathlib import Path
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from foundation.common_types.fqns.fqn import ModuleFqn
from typer import Argument

from architecture.application.commands.create_package import CreatePackageCommand
from architecture.domain.enums.architecture_layer import ArchitectureLayer
from architecture.infrastructure.message_bus import MessageBus

_SUB_PACKAGES = {
    ArchitectureLayer.DOMAIN: [
        "aggregates",
        "value_objects",
        "entities",
        "ports",
        "repositories",
        "serivces",
        "identities",
        "events",
        "exceptions",
        "enums",
    ],
    ArchitectureLayer.APPLICATION: [
        "commands",
        "queries",
        "event_handlers",
        "dtos",
        "ports",
    ],
    ArchitectureLayer.INFRASTRUCTURE: [
        "adapters",
        "repositories",
    ],
}


@inject
def _create_package(
    cmd: CreatePackageCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def init_context(
    context: Annotated[
        str, Argument(help="Context FQN to create (要创建的上下文 FQN)")
    ],
) -> None:
    # 1. Use uv to initialize the context library
    subprocess.run(
        ["uv", "init", "--lib", f"contexts/{context}"], cwd=str(Path.cwd()), check=True
    )

    # 2. Scaffold DDD directories
    fqns: list[ModuleFqn] = [ModuleFqn(context)]

    for layer in ArchitectureLayer:
        fqn = ModuleFqn(f"{context}.{layer.value}")
        fqns.append(fqn)

        for package in _SUB_PACKAGES.get(layer, []):
            fqns.append(ModuleFqn(f"{fqn}.{package}"))

    for fqn in fqns:
        cmd = CreatePackageCommand(fqn=fqn)
        _create_package(cmd)

    # 3. Add to workspace root pyproject.toml dependencies
    project_name = context.replace("_", "-")
    subprocess.run(["uv", "add", project_name], cwd=str(Path.cwd()), check=True)
