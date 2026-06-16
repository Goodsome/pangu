from pathlib import Path
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Dependency
from dependency_injector.providers import Dict
from dependency_injector.providers import Factory
from dependency_injector.providers import List
from dependency_injector.providers import Singleton
from redis.asyncio import Redis
from codegen.code_dom.application.commands.generate_code import GenerateCodeHandler
from codegen.code_dom.application.queries.get_code_document_diff import (
    GetCodeDocumentDiffHandler,
)
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
)
from codegen.code_metadata.application.commands.clean_node import CleanNodeCommand
from codegen.code_metadata.application.commands.clean_node import CleanNodeHandler
from codegen.code_metadata.application.commands.clean_unused_nodes import (
    CleanUnusedNodesCommand,
)
from codegen.code_metadata.application.commands.clean_unused_nodes import (
    CleanUnusedNodesHandler,
)
from codegen.code_metadata.application.commands.delete_module_in_physical import (
    DeleteModuleInPhysicalCommand,
)
from codegen.code_metadata.application.commands.delete_module_in_physical import (
    DeleteModuleInPhysicalHandler,
)
from codegen.code_metadata.application.commands.generate_code import GenerateCode
from codegen.code_metadata.application.commands.generate_code import GenerateCodeCommand
from codegen.code_metadata.application.commands.ingest_project import IngestProject
from codegen.code_metadata.application.event_handlers.on_batch_nodes_deleted import (
    OnBatchNodesDeleted,
)
from codegen.code_metadata.application.event_handlers.on_node_deleted import (
    OnNodeDeleted,
)
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
from codegen.code_metadata.application.queries.trace_symbol_dependencies import (
    TraceSymbolDependenciesQueryHandler,
)
from codegen.code_metadata.domain.domain_events.node_deleted import NodeDeleted
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.code_metadata.infrastructure.gateways.file_system_code_graph_builder import (
    FileSystemCodeGraphBuilder,
)
from codegen.code_metadata.infrastructure.gateways.file_system_file_differ import (
    FileSystemFileDiffer,
)
from codegen.code_metadata.infrastructure.gateways.python_code_generator import (
    PythonCodeGenerator,
)
from codegen.code_metadata.infrastructure.message_bus import MessageBus
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_code_node_query_service import (
    SqlAlchemyCodeNodeQueryService,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_code_node_repository import (
    SqlAlchemyCodeNodeRepository,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_code_node_sync_service import (
    SqlAlchemyCodeNodeSyncService,
)
from codegen.shared.application.integration_events.batch_nodes_deleted import (
    BatchNodesDeletedIntegrationEvent,
)
from codegen.shared.application.integration_events.node_deleted import (
    NodeDeletedIntegrationEvent,
)
from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.infrastructure.adapters.sql_alchemy_unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.gateways.redis_stream_subscriber import (
    RedisStreamSubscriber,
)


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    database: Dependency[Database] = Dependency(instance_of=Database)
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
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
    code_node_repository_factory: Factory[SqlAlchemyCodeNodeRepository] = Factory(
        SqlAlchemyCodeNodeRepository
    )
    code_node_unit_of_work: Factory[SqlAlchemyUnitOfWork[CodeNodeRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=code_node_repository_factory.provider,
    )
    python_code_generator: Factory[PythonCodeGenerator] = Factory(
        PythonCodeGenerator, generate_code_handler=generate_code_handler
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
    generate_code: Factory[GenerateCode] = Factory(
        GenerateCode,
        query_service=code_node_query_service,
        code_generator=python_code_generator,
    )
    clean_node: Factory[CleanNodeHandler] = Factory(
        CleanNodeHandler,
        query_service=code_node_query_service,
        sync_service=code_node_sync_service,
    )
    clean_unused_nodes: Factory[CleanUnusedNodesHandler] = Factory(
        CleanUnusedNodesHandler,
        query_service=code_node_query_service,
        sync_service=code_node_sync_service,
    )
    ingest_project: Factory[IngestProject] = Factory(
        IngestProject,
        graph_builder=code_graph_builder,
        sync_service=code_node_sync_service,
        query_service=code_node_query_service,
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
    delete_module_in_physical_handler: Factory[DeleteModuleInPhysicalHandler] = Factory(
        DeleteModuleInPhysicalHandler, file_system=file_system_port
    )
    on_node_deleted_handler: Singleton[OnNodeDeleted] = Singleton(OnNodeDeleted)
    on_batch_nodes_deleted: Singleton[OnBatchNodesDeleted] = Singleton(
        OnBatchNodesDeleted
    )
    message_bus: Factory[MessageBus] = Factory(
        MessageBus,
        uow=code_node_unit_of_work,
        command_handlers=Dict(
            {
                CleanNodeCommand: clean_node.provided.execute,
                CleanUnusedNodesCommand: clean_unused_nodes.provided.execute,
                GenerateCodeCommand: generate_code.provided.execute,
                DeleteModuleInPhysicalCommand: delete_module_in_physical_handler.provided.execute,
            }
        ),
        event_handlers=Dict(
            {
                NodeDeleted: List(on_node_deleted_handler.provided.send_to_outbox),
                NodeDeletedIntegrationEvent: List(
                    on_node_deleted_handler.provided.handle_clean_node
                ),
                BatchNodesDeletedIntegrationEvent: List(
                    on_batch_nodes_deleted.provided.handle_nodes_deleted
                ),
            }
        ),
    )
    event_registry: Singleton[EventRegistry] = Singleton(EventRegistry.init)
    redis_subscriber: Singleton[RedisStreamSubscriber] = Singleton(
        RedisStreamSubscriber,
        client=redis_client,
        message_bus_factory=message_bus.provider,
        registry=event_registry,
        service_name="code_metadata",
        subscriptions=List("code_node_events"),
    )
