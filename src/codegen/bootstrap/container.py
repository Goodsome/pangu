from dependency_injector import containers
from dependency_injector.providers import Singleton
from dependency_injector.providers import Container
from dependency_injector.providers import Configuration
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem
from codegen.shared.container import Container as SharedContainer
from codegen.code_metadata.container import Container as CodeMetadataContainer
from codegen.code_dom.container import Container as CodeDomContainer


class AppContainer(containers.DeclarativeContainer):
    config: Configuration = Configuration()
    os_file_system: Singleton[OSFileSystem] = Singleton(
        OSFileSystem, root=config.project_root, encoding=config.encoding
    )
    shared_container: Container[SharedContainer] = Container(
        SharedContainer, config=config.shared
    )
    code_dom_container: Container[CodeDomContainer] = Container(
        CodeDomContainer, file_system_port=os_file_system
    )
    code_metadata_container: Container[CodeMetadataContainer] = Container(
        CodeMetadataContainer,
        database=shared_container.database,
        file_system_port=os_file_system,
        project_root=config.project_root,
        get_project_documents=code_dom_container.get_project_documents,
        get_code_document_diff=code_dom_container.get_code_document_diff,
        generate_code_handler=code_dom_container.generate_code_handler,
    )