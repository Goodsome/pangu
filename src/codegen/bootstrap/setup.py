from pathlib import Path
from codegen.bootstrap.container import AppContainer
from codegen.bootstrap.config import AppConfig
from codegen.bootstrap.config import load_all_configurations


def create_container(
    config_override: AppConfig | None = None, init_resources: bool = True
) -> AppContainer:
    """Bootstrap the DI container with configuration."""
    container = AppContainer()
    cwd = Path.cwd()
    container.config.project_root.from_value(cwd)
    container.config.encoding.from_value("utf-8")
    container.config.config_path.from_value(cwd / "codegen.yaml")
    app_config = config_override or load_all_configurations()
    container.config.from_pydantic(app_config)
    if init_resources:
        container.init_resources()
    return container
