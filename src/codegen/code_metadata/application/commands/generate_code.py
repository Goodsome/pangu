import logging
from dataclasses import dataclass
from codegen.code_metadata.application.dtos.generate_code_result import (
    GenerateCodeResult,
)
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.command import Command

logger = logging.getLogger(__name__)


class GenerateCodeCommand(Command):
    fqns: list[str]


@dataclass
class GenerateCode:
    query_service: CodeNodeQueryService
    code_generator: CodeGenerator

    def execute(
        self, cmd: GenerateCodeCommand, _uow: UnitOfWork[CodeNodeRepository]
    ) -> GenerateCodeResult:
        nodes = self.query_service.find_by_fqn_prefixs(cmd.fqns)
        registry = NodeRegistry.create(nodes=nodes)
        self.code_generator.generate_code_by_nodes(nodes=nodes, node_registry=registry)
        return GenerateCodeResult(code="success")
