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


@dataclass
class ProjectSyncService:
    parser: CodeParser
    file_system_port: FileSystemPort
    component_policy_factory: ComponentPolicyFactory
    uow: UnitOfWork[ComponentRepository]
    path_parser: PathParser
    module_uow: UnitOfWork[ModuleRepository]

    def get_component(self, context: str, component_name: str) -> Component | None:
        with self.uow:
            components = self.uow.repository.find_by_context_names(
                {(context, component_name)}
            )
            return components.get((context, component_name))

    def get_module(self, path: str) -> Module | None:
        with self.module_uow:
            paths = {path}
            module = self.module_uow.repository.find_by_paths(paths)
            return module.get(path)

    def list_modules(self, current: int = 1, size: int = 10) -> Page[Module]:
        with self.module_uow:
            page_query = PageQuery[ModuleFilter](
                current=current, size=size, condition=ModuleFilter()
            )
            return self.module_uow.repository.find_page(page_query)

    def reverse_code(
        self, context: str, component_type: str | None, component_name: str | None
    ):
        scan_payload = self._discover_files(
            context_name=context,
            component_type=ComponentType(component_type) if component_type else None,
            mudule_name=component_name,
        )
        parsed_modules = self._parse_scan_payload(scan_payload)
        existing_modules = self._get_existing_modules(parsed_modules)
        module_registry = ModuleRegistry(init_modules=existing_modules)
        sync_context = SyncProjectContext(
            registry=module_registry, path_parser=self.path_parser
        )
        sync_modules = sync_context.sync_parsed_modules(parsed_modules)
        self._save_modules(sync_modules.values())

    def _save_modules(self, sync_modules: Iterable[Module]) -> None:
        with self.module_uow:
            for module in sync_modules:
                self.module_uow.repository.save(module)
            self.module_uow.commit()
        logger.info(f"save {len(list(sync_modules))} modules")

    def _get_existing_modules(self, parsed_modules: list[ParsedModule]) -> list[Module]:
        module_paths: set[str] = set()
        for parsed_module in parsed_modules:
            module_paths.add(parsed_module.import_path)
            module_paths.update(parsed_module.dependency_modules())
            module_paths.update(parsed_module.father_paths())
        with self.module_uow:
            modules = self.module_uow.repository.find_by_paths(paths=module_paths)
        return list(modules.values())

    def _discover_files(
        self,
        context_name: str,
        component_type: ComponentType | None,
        mudule_name: str | None,
    ) -> ScanPayload:
        base_dir = self._get_base_dir(context_name)
        pattern = self._get_include_pattern(
            component_type=component_type, mudule_name=mudule_name
        )
        raw_scan_payloads: list[ScanResult] = []
        for file_path in self.file_system_port.list_directory_recursively(
            path=base_dir, pattern=pattern
        ):
            raw_scan_payloads.append(
                FileScanResult(
                    name=file_path.stem, path=file_path, extension=file_path.suffix
                )
            )
        return ScanPayload(result=raw_scan_payloads)

    def _get_base_dir(self, context_name: str) -> Path:
        base_dir = Path("src/codegen") / context_name
        return base_dir

    def _get_include_pattern(
        self, component_type: ComponentType | None, mudule_name: str | None
    ) -> str:
        pattern = "*.py"
        if mudule_name is not None:
            pattern = f"{mudule_name}.py"
        if component_type is not None:
            policy = self.component_policy_factory.get_policy(
                ComponentType(component_type)
            )
            pattern = f"{policy.dir_name}/{pattern}"
        return pattern

    def _parse_scan_payload(self, scan_payload: ScanPayload) -> list[ParsedModule]:
        result: list[ParsedModule] = []
        for scan_result in scan_payload.result:
            parsed_module = self._parse_scan_result(scan_result)
            result.append(parsed_module)
        return result

    def _parse_scan_result(self, scan_result: ScanResult) -> ParsedModule:
        match scan_result:
            case FileScanResult(name="__init__"):
                return self._parse_init_file(scan_result)
            case FileScanResult():
                return self._parse_file_scan_result(scan_result)
            case _:
                assert_never(scan_result)

    def _parse_init_file(self, scan_result: FileScanResult) -> ParsedDirectoryModule:
        path = scan_result.path
        code = self.file_system_port.read_file(path)
        return self.parser.parse_init_module(code, path)

    def _parse_file_scan_result(self, scan_result: FileScanResult) -> ParsedFileModule:
        path = scan_result.path
        code = self.file_system_port.read_file(path)
        return self.parser.parse_module(code, path)

    def _collect_files(
        self, context: str, component_type: str | None, component_name: str | None
    ) -> list[FileCollection]:
        result: list[FileCollection] = []
        path = Path(f"src/codegen/{context}")
        pattern = "*.py"
        if component_name is not None:
            pattern = f"{SnakeString(component_name)}.py"
        if component_type is not None:
            policy = self.component_policy_factory.get_policy(
                ComponentType(component_type)
            )
            pattern = f"{policy.dir_name}/{pattern}"
        for file_path in self.file_system_port.list_directory_recursively(
            path=path, pattern=pattern
        ):
            if "interfaces" in str(file_path):
                continue
            file_name = file_path.stem
            if file_name in [
                "__init__",
                "container",
                "expr_def",
                "parsed_expr",
                "_convert",
                "match_pattern",
            ]:
                continue
            code = self.file_system_port.read_file(file_path)
            parsed_path = self.path_parser.parse_file_path(file_path)
            parsed_component = self.parser.parse(
                code=code, component_name=PascalString(file_name)
            )
            reference_sources = self._collect_reference_sources(
                file_path, parsed_component
            )
            result.append(
                FileCollection(
                    context=parsed_path.context,
                    code=code,
                    type=parsed_path.component_type,
                    layer=parsed_path.layer,
                    name=PascalString(file_name),
                    path=file_path,
                    parsed_component=parsed_component,
                    reference_sources=reference_sources,
                )
            )
        return result

    def _collect_reference_sources(
        self, file_path: Path, parsed_component: ParsedComponent
    ) -> list[ReferenceSource]:
        reference_sources: list[ReferenceSource] = []
        for import_dto in parsed_component.imports:
            if import_dto.level == 0:
                module = import_dto.module or ""
            else:
                parts = file_path.parts[: -import_dto.level]
                module = ".".join(parts) + "." + (import_dto.module or "")
            parsed_path = self.path_parser.parse_module_path(module)
            reference_sources.append(
                ReferenceSource(
                    context=parsed_path.context, components=import_dto.names
                )
            )
        return reference_sources

    def _get_existing_components(
        self, file_collections: list[FileCollection]
    ) -> dict[tuple[str, str], Component]:
        context_names: set[tuple[str, str]] = set()
        contexts_only: set[str] = set()
        for fc in file_collections:
            context_names.add((fc.context, fc.name))
            context_names.update(fc.collect_dependency_components())
            contexts_only.update(fc.collect_dependency_contexts_only())
        with self.uow:
            existing_components = self.uow.repository.find_by_context_names(
                context_names=context_names
            )
            existing_dependencies_by_context = self.uow.repository.find_by_contexts(
                contexts=contexts_only
            )
            existing_components.update(existing_dependencies_by_context)
        return existing_components

    def _sync_components(
        self,
        file_collections: list[FileCollection],
        existing_components: dict[tuple[str, str], Component],
    ) -> None:
        id_maps = {c.id: c for c in existing_components.values()}
        component_collection = MemoryComponentCollection(
            store=existing_components, components=id_maps
        )
        for f in file_collections:
            component_kind = (
                ComponentKind.UNION
                if f.parsed_component.is_union
                else ComponentKind.CLASS
            )
            component = component_collection.get_or_create_component(
                f.context, f.name, component_kind=component_kind
            )
            resolver = ReferenceResolver(
                component=component,
                components=component_collection,
                reference_sources=f.reference_sources,
            )
            mapper = ParsedComponentToSyncData(resolver=resolver)
            component_sync_data = mapper.map(
                context=f.context,
                parsed_component=f.parsed_component,
                component_type=f.type,
                layer=f.layer,
            )
            component.update(component_sync_data=component_sync_data)
            component_collection.update(component=component)
        with self.uow:
            for component in component_collection.need_saves.values():
                self.uow.repository.save(component)
            self.uow.commit()
