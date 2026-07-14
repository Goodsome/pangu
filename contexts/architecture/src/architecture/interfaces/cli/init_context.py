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


def _create_context_pyproject(context: str):
    context_dir = Path.cwd() / "contexts" / context
    context_dir.mkdir(parents=True, exist_ok=True)
    pyproject_path = context_dir / "pyproject.toml"
    if not pyproject_path.exists():
        content = f"""[project]
name = "{context}"
version = "0.1.0"
description = ""
requires-python = ">=3.14"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{context}"]

[tool.pyright]
venvPath = "../../"
venv = ".venv"
include = ["src"]
extraPaths = ["src", "../../src"]
reportUnusedCallResult = "none"
"""
        pyproject_path.write_text(content)


def _update_root_pyproject(context: str):
    root_pyproject = Path.cwd() / "pyproject.toml"
    if not root_pyproject.exists():
        return
    content = root_pyproject.read_text()

    # Add to dependencies if not there
    if f'"{context}",' not in content and f'"{context}"' not in content:
        import re

        # Find the dependencies list and append
        content = re.sub(
            r"(dependencies\s*=\s*\[)([^\]]*?)(\n\])",
            rf'\1\2\n    "{context}",\3',
            content,
            count=1,
        )

    # Add to tool.uv.sources
    source_line = f"{context} = {{ workspace = true }}"
    if source_line not in content:
        if "[tool.uv.sources]" in content:
            content = content.replace(
                "[tool.uv.sources]", f"[tool.uv.sources]\n{source_line}", 1
            )
        else:
            content += f"\n[tool.uv.sources]\n{source_line}\n"

    root_pyproject.write_text(content)


def _run_uv_sync():
    subprocess.run(["uv", "sync"], cwd=str(Path.cwd()))


def init_context(
    context: Annotated[
        str, Argument(help="Context FQN to create (要创建的上下文 FQN)")
    ],
) -> None:
    fqns: list[ModuleFqn] = [ModuleFqn(context)]

    for layer in ArchitectureLayer:
        fqn = ModuleFqn(f"{context}.{layer.value}")
        fqns.append(fqn)

        for package in _SUB_PACKAGES.get(layer, []):
            fqns.append(ModuleFqn(f"{fqn}.{package}"))

    for fqn in fqns:
        cmd = CreatePackageCommand(fqn=fqn)
        _create_package(cmd)

    # Automatically scaffold pyproject.toml and sync uv workspace
    _create_context_pyproject(context)
    _update_root_pyproject(context)
    _run_uv_sync()
