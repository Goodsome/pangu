import argparse
from enum import StrEnum, auto
import subprocess
from dataclasses import dataclass
from pathlib import Path

class PackageType(StrEnum):
    PACKAGES = auto()
    CONTEXTS = auto()

@dataclass
class Config:
    package_name: str
    package_type: PackageType


def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "package_type",
        type=PackageType,
    )
    parser.add_argument(
        "package_name",
        type=str,
    )
    args = parser.parse_args()
    return Config(**vars(args))


def main():
    config = parse_args()
    subprocess.run(
        ["uv", "init", "--lib", f"{config.package_type}/{config.package_name}"],
        cwd=str(Path.cwd()),
        check=True,
    )

    package_name = config.package_name.replace("_", "-")
    subprocess.run(
        ["uv", "add", package_name],
        cwd=str(Path.cwd()),
        check=True,
    )

if __name__ == "__main__":
    main()