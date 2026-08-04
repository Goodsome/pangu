import argparse
from pathlib import Path

from architecture.domain.services.fqn_service import FqnService
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.system.os_file_system import OSFileSystem
from pydantic.dataclasses import dataclass

from architecture.domain.enums.architecture_layer import ArchitectureLayer

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


def init_context(
    context: str,
) -> None:
    fqns: list[ModuleFqn] = [ModuleFqn(context)]

    for layer in ArchitectureLayer:
        fqn = ModuleFqn(f"{context}.{layer.value}")
        fqns.append(fqn)

        for package in _SUB_PACKAGES.get(layer, []):
            fqns.append(ModuleFqn(f"{fqn}.{package}"))

    fs = OSFileSystem(root=Path.home() / "code/pangu")
    for fqn in fqns:
        path = FqnService.build_path(fqn, is_package=True) / "__init__.py"
        fs.write_file(path=path, content="")


@dataclass
class Config:
    context_name: str


def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "context_name",
    )
    args = parser.parse_args()
    return Config(**vars(args))

def main():
    config = parse_args()
    init_context(config.context_name)

if __name__ == "__main__":
    main()