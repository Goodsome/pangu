from pathlib import Path
from architecture.container import Container as ArchitectureContainer
from code_generation.container import Container as CodeGenerationContainer
from code_structure.container import Container as CodeStructureContainer
from dependency_injector import containers
from dependency_injector.providers import Configuration, Container, Singleton
from pangu_cli.bootstrap.config import AppConfig, load_all_configurations
from code_dom.container import Container as CodeDomContainer
from pangu_cli.infrastructure.container import Container as SharedContainer
from foundation.system.os_file_system import OSFileSystem


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
    architecture_container: Container[ArchitectureContainer] = Container(
        ArchitectureContainer,
        db_driver=shared_container.db_driver,
        file_system_port=os_file_system,
        redis_client=shared_container.redis_client,
    )
    code_structure_container: Container[CodeStructureContainer] = Container(
        CodeStructureContainer,
        db_driver=shared_container.db_driver,
        redis_client=shared_container.redis_client,
        get_file_document_handler=code_dom_container.get_file_document_handler,
    )
    code_generation_container: Container[CodeGenerationContainer] = Container(
        CodeGenerationContainer,
        code_dom_api=code_dom_container.api,
        code_structure_api=code_structure_container.api,
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
