from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Dependency
from dependency_injector.providers import Factory
from dependency_injector.providers import Singleton
from codegen.code_dom.application.commands.generate_code import GenerateCodeHandler
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
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
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
