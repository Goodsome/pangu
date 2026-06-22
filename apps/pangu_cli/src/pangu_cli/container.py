from pathlib import Path

from architecture.container import Container as ArchitectureContainer
from dependency_injector import containers
from dependency_injector.providers import Configuration, Container, Singleton

from codegen.bootstrap.config import AppConfig, load_all_configurations
from codegen.code_dom.container import Container as CodeDomContainer
from codegen.code_metadata.container import Container as CodeMetadataContainer
from codegen.shared.container import Container as SharedContainer
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem


class AppContainer(containers.DeclarativeContainer):
    config: Configuration = Configuration()
    os_file_system: Singleton[OSFileSystem] = Singleton(
        OSFileSystem, root=config.project_root, encoding=config.encoding
    )
    shared_container: Container[SharedContainer] = Container(
        SharedContainer, config=config.shared
    )
    code_dom_container: Container[CodeDomContainer] = Container(
        CodeDomContainer,
        file_system_port=os_file_system,
        redis_client=shared_container.redis_client,
    )
    code_metadata_container: Container[CodeMetadataContainer] = Container(
        CodeMetadataContainer,
        database=shared_container.database,
        file_system_port=os_file_system,
        project_root=config.project_root,
        get_project_documents=code_dom_container.get_project_documents,
        get_code_document_diff=code_dom_container.get_code_document_diff,
        generate_code_handler=code_dom_container.generate_code_handler,
        redis_client=shared_container.redis_client,
    )
    architecture_container: Container[ArchitectureContainer] = Container(
        ArchitectureContainer,
        file_system_port=os_file_system,
        redis_client=shared_container.redis_client,
    )


async def create_container(
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
        _init = container.init_resources()
        if _init:
            await _init
    return container
