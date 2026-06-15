from dataclasses import dataclass
from pydantic import BaseModel
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class SyncModuleCommand(BaseModel):
    module_fqn: str
