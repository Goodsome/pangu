import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    package_name: str


def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "package_name",
        type=str,
    )
    args = parser.parse_args()
    return Config(**vars(args))


def main():
    config = parse_args()
    subprocess.run(
        ["uv", "init", "--lib", f"packages/{config.package_name}"],
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