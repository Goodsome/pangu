from pathlib import Path
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Dependency
from dependency_injector.providers import Factory
from dependency_injector.providers import Singleton
from event_hub import EventHub
from codegen.code_dom.application.commands.generate_code import GenerateCodeHandler
from codegen.code_metadata.application.commands.delete_component import DeleteComponent
from codegen.code_metadata.application.commands.generate_code import GenerateCode
from codegen.code_metadata.application.commands.ingest_project import IngestProject
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.application.ports.file_differ import FileDiffer
from codegen.code_metadata.application.queries.find_unused_nodes import FindUnusedNodes
from codegen.code_metadata.application.queries.get_code_node_detail import (
    GetCodeNodeDetail,
)
from codegen.code_metadata.application.queries.get_dev_progress import (
    GetDevProgressHandler,
)
from codegen.code_metadata.application.queries.get_directory_tree import (
    GetDirectoryTree,
)
from codegen.code_metadata.application.queries.list_components import ListComponents
from codegen.code_metadata.application.queries.trace_symbol_dependencies import (
    TraceSymbolDependenciesQueryHandler,
)
from codegen.code_metadata.application.services.dev_progress_service import (
    DevProgressService,
)
from codegen.code_metadata.application.services.project_sync_service import (
    ProjectSyncService,
)
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.domain.ports.module_repository import ModuleRepository
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.infrastructure.gateways.file_system_code_graph_builder import (
    FileSystemCodeGraphBuilder,
)
from codegen.code_metadata.infrastructure.gateways.file_system_file_differ import (
    FileSystemFileDiffer,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_code_node_query_service import (
    SqlAlchemyCodeNodeQueryService,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_code_node_sync_service import (
    SqlAlchemyCodeNodeSyncService,
)
from codegen.code_metadata.infrastructure.gateways.python_code_generator import (
    PythonCodeGenerator,
)
from codegen.code_metadata.infrastructure.gateways.python_code_parser import (
    PythonCodeParser,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_component_query_service import (
    SqlAlchemyComponentQueryService,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_component_repository import (
    SqlAlchemyComponentRepository,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_module_query_service import (
    SqlAlchemyModuleQueryService,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_module_repository import (
    SqlAlchemyModuleRepository,
)
from codegen.code_dom.application.queries.get_code_document_diff import (
    GetCodeDocumentDiffHandler,
)
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.adapters.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    database: Dependency[Database] = Dependency(instance_of=Database)
    event_hub: Dependency[EventHub] = Dependency(instance_of=EventHub)
    event_publisher_factory = Dependency()
    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )
    project_root: Dependency[Path] = Dependency(instance_of=Path)
    get_project_documents: Dependency[GetProjectDocumentsHandler] = Dependency(
        instance_of=GetProjectDocumentsHandler
    )
    get_code_document_diff: Dependency[GetCodeDocumentDiffHandler] = Dependency(
        instance_of=GetCodeDocumentDiffHandler
    )
    generate_code_handler: Dependency[GenerateCodeHandler] = Dependency(
        instance_of=GenerateCodeHandler
    )
    component_repository_factory: Factory[SqlAlchemyComponentRepository] = Factory(
        SqlAlchemyComponentRepository
    )
    module_repository_factory: Factory[SqlAlchemyModuleRepository] = Factory(
        SqlAlchemyModuleRepository
    )
    component_query_service: Factory[SqlAlchemyComponentQueryService] = Factory(
        SqlAlchemyComponentQueryService,
        session_factory=database.provided.session_factory,
    )
    module_query_service: Factory[SqlAlchemyModuleQueryService] = Factory(
        SqlAlchemyModuleQueryService, session_factory=database.provided.session_factory
    )
    unit_of_work: Factory[SqlAlchemyUnitOfWork[ComponentRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=component_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )
    module_unit_of_work: Factory[SqlAlchemyUnitOfWork[ModuleRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=module_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )
    component_policy_factory: Singleton[ComponentPolicyFactory] = Singleton(
        ComponentPolicyFactory
    )
    python_code_parser: Factory[PythonCodeParser] = Factory(PythonCodeParser)
    python_code_generator: Factory[PythonCodeGenerator] = Factory(
        PythonCodeGenerator,
        component_policy_factory=component_policy_factory,
        generate_code_handler=generate_code_handler,
    )
    path_parser: Factory[PathParser] = Factory(
        PathParser,
        dir_to_type_registry=component_policy_factory.provided.get_dir_to_type_registry.call(),
    )
    code_graph_builder: Factory[CodeGraphBuilder] = Factory(
        FileSystemCodeGraphBuilder, get_project_documents=get_project_documents
    )
    code_node_sync_service: Factory[CodeNodeSyncService] = Factory(
        SqlAlchemyCodeNodeSyncService, session_factory=database.provided.session_factory
    )
    code_node_query_service: Factory[CodeNodeQueryService] = Factory(
        SqlAlchemyCodeNodeQueryService,
        session_factory=database.provided.session_factory,
    )
    list_components: Factory[ListComponents] = Factory(
        ListComponents, query_service=component_query_service
    )
    generate_code: Factory[GenerateCode] = Factory(
        GenerateCode,
        query_service=code_node_query_service,
        code_generator=python_code_generator,
    )
    delete_component: Factory[DeleteComponent] = Factory(
        DeleteComponent, uow=unit_of_work
    )
    ingest_project: Factory[IngestProject] = Factory(
        IngestProject,
        graph_builder=code_graph_builder,
        sync_service=code_node_sync_service,
        query_service=code_node_query_service,
    )
    dev_progress_service: Factory[DevProgressService] = Factory(
        DevProgressService,
        file_system_port=file_system_port,
        generator=python_code_generator,
        uow=module_unit_of_work,
        path_parser=path_parser,
    )
    get_directory_tree: Factory[GetDirectoryTree] = Factory(
        GetDirectoryTree, query_service=code_node_query_service
    )
    get_code_node_detail: Factory[GetCodeNodeDetail] = Factory(
        GetCodeNodeDetail, query_service=code_node_query_service
    )
    trace_symbol_dependencies: Factory[TraceSymbolDependenciesQueryHandler] = Factory(
        TraceSymbolDependenciesQueryHandler, query_service=code_node_query_service
    )
    find_unused_nodes: Factory[FindUnusedNodes] = Factory(
        FindUnusedNodes, query_service=code_node_query_service
    )
    file_differ: Factory[FileDiffer] = Factory(
        FileSystemFileDiffer, handler=get_code_document_diff
    )
    get_dev_progress: Factory[GetDevProgressHandler] = Factory(
        GetDevProgressHandler,
        query_service=code_node_query_service,
        file_differ=file_differ,
    )
    project_sync_service: Factory[ProjectSyncService] = Factory(
        ProjectSyncService,
        parser=python_code_parser,
        file_system_port=file_system_port,
        component_policy_factory=component_policy_factory,
        uow=unit_of_work,
        path_parser=path_parser,
        module_uow=module_unit_of_work,
    )
