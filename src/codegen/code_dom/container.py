from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dict, List
from dependency_injector.providers import Dependency
from dependency_injector.providers import Factory
from dependency_injector.providers import Singleton
from redis.asyncio import Redis
from codegen.code_dom.application.commands.generate_code import GenerateCodeHandler
from codegen.code_dom.application.event_handlers.on_module_created import OnModuleCreated
from codegen.code_dom.application.event_handlers.on_module_deleted import OnModuleDeleted
from codegen.code_dom.application.event_handlers.on_module_moved import OnModuleMoved
from codegen.code_dom.application.queries.get_code_document_diff import (
    GetCodeDocumentDiffHandler,
)
from codegen.code_dom.application.queries.get_file_document import (
    GetFileDocumentHandler,
)
from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
)
from codegen.code_dom.domain.ports.code_generator import CodeGenerator
from codegen.code_dom.domain.ports.code_parser import CodeParser
from codegen.code_dom.domain.ports.code_similarity_calculator import (
    CodeSimilarityCalculator,
)
from codegen.code_dom.infrastructure.gateways.ast_code_generator import AstCodeGenerator
from codegen.code_dom.infrastructure.gateways.ast_code_parser import ASTCodeParser
from codegen.code_dom.infrastructure.gateways.ast_code_similarity_calculator import (
    AstCodeSimilarityCalculator,
)
from codegen.code_dom.infrastructure.gateways.black_code_formatter import (
    BlackCodeFormatter,
)
from codegen.code_dom.infrastructure.gateways.ruff_code_formmater import RuffCodeFormatter
from codegen.code_dom.infrastructure.repositories.file_system_codebase_repository import FileSystemCodebaseRepository
from codegen.code_dom.infrastructure.repositories.file_system_document_repository import FileSystemDocumentRepository
from codegen.code_dom.infrastructure.repositories.file_system_unit_of_work import FileSystemUnitOfWork
from codegen.shared.application.integration_events.module_created import ModuleCreatedIntegrationEvent
from codegen.shared.application.integration_events.module_deleted import ModuleDeletedIntegrationEvent
from codegen.shared.application.integration_events.module_moved import ModuleMovedIntegrationEvent
from codegen.shared.application.integration_events.registry import EventRegistry
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.infrastructure.gateways.redis_stream_subscriber import RedisStreamSubscriber
from codegen.shared.infrastructure.message_bus import BaseMessageBus


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    
    redis_client: Dependency[Redis] = Dependency(instance_of=Redis)
    
    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )
    code_parser: Factory[CodeParser] = Factory(
        ASTCodeParser, file_system=file_system_port
    )
    black_code_formatter: Singleton[BlackCodeFormatter] = Singleton(BlackCodeFormatter)
    get_project_documents: Factory[GetProjectDocumentsHandler] = Factory(
        GetProjectDocumentsHandler, code_parser=code_parser
    )
    get_file_document: Factory[GetFileDocumentHandler] = Factory(
        GetFileDocumentHandler, code_parser=code_parser
    )
    code_generator: Factory[CodeGenerator] = Factory(AstCodeGenerator)
    code_similarity_calculator: Factory[CodeSimilarityCalculator] = Factory(
        AstCodeSimilarityCalculator
    )
    get_code_document_diff: Factory[GetCodeDocumentDiffHandler] = Factory(
        GetCodeDocumentDiffHandler,
        code_generator=code_generator,
        file_system=file_system_port,
        code_similarity_calculator=code_similarity_calculator,
    )
    generate_code_handler: Factory[GenerateCodeHandler] = Factory(
        GenerateCodeHandler,
        code_generator=code_generator,
        file_system=file_system_port,
        code_formatter=black_code_formatter,
    )

    codebase_repository: Factory[FileSystemCodebaseRepository] = Factory(
        FileSystemCodebaseRepository,
        file_system=file_system_port,
    )

    ruff_code_formatter: Singleton[RuffCodeFormatter] = Singleton(
        RuffCodeFormatter,
    )

    document_repository: Factory[FileSystemDocumentRepository] = Factory(
        FileSystemDocumentRepository,
        file_system=file_system_port,
        code_formatter=ruff_code_formatter,
    )
    
    unit_of_work: Factory[FileSystemUnitOfWork] = Factory(
        FileSystemUnitOfWork,
        codebase_repository=codebase_repository,
        document_repository=document_repository,
    )

    on_module_created: Singleton[OnModuleCreated] = Singleton(
        OnModuleCreated,
        file_system=file_system_port,
    )

    on_module_deleted: Singleton[OnModuleDeleted] = Singleton(
        OnModuleDeleted,
        file_system=file_system_port,
    )

    on_module_moved: Singleton[OnModuleMoved] = Singleton(
        OnModuleMoved,
        file_system=file_system_port,
    )

    message_bus: Factory[BaseMessageBus] = Factory(
        BaseMessageBus,
        uow=unit_of_work,
        command_handlers=Dict(),
        event_handlers=Dict(
            {
                ModuleCreatedIntegrationEvent: List(
                    on_module_created.provided.create_file,
                ),
                ModuleDeletedIntegrationEvent: List(
                    on_module_deleted.provided.clean_filesystem,
                ),
                ModuleMovedIntegrationEvent: List(
                    on_module_moved.provided.execute_physical_move,
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
        service_name="code_dom",
        subscriptions=List("architecture_events"),
    )
