from collections.abc import Iterable
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import assert_never
from codegen.code_metadata.application.contexts.sync_project_context import (
    SyncProjectContext,
)
from codegen.code_metadata.application.dtos.file_collection import FileCollection
from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_module import ParsedDirectoryModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedModule
from codegen.code_metadata.application.dtos.scan_payload import ScanPayload
from codegen.code_metadata.application.dtos.scan_result import FileScanResult
from codegen.code_metadata.application.dtos.scan_result import ScanResult
from codegen.code_metadata.application.mappers.parsed_component_to_sync_data import (
    ParsedComponentToSyncData,
)
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.application.services.memory_component_collection import (
    MemoryComponentCollection,
)
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_kind import ComponentKind
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.domain.ports.module_repository import ModuleRepository
from codegen.code_metadata.domain.registries.module_registry import ModuleRegistry
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.reference_source import ReferenceSource
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString

logger = logging.getLogger(__name__)
