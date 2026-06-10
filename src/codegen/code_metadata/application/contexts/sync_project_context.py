from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.application.contexts.sync_module_context import (
    SyncModuleContext,
)
from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_module import ParsedDirectoryModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedModule
from codegen.code_metadata.domain.aggregates.module import ExternalModule
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.module import DirectoryModule
from codegen.code_metadata.domain.aggregates.module import FileModule
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.registries.component_registry import ComponentRegistry
from codegen.code_metadata.domain.registries.module_registry import ModuleRegistry
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.domain.value_objects.module_dependency import (
    ModuleDependency,
)
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget


@dataclass
class SyncProjectContext:
    registry: ModuleRegistry
    sync_modules: dict[ModuleId, Module] = field(init=False)
    path_parser: PathParser

    def __post_init__(self):
        self.sync_modules = {}
        self.registry.on_module_registered = self.mark_for_sync

    def mark_for_sync(self, module: Module) -> None:
        self.sync_modules[module.id] = module

    def sync_parsed_modules(
        self, parsed_modules: list[ParsedModule]
    ) -> dict[ModuleId, Module]:
        modules: list[Module] = []
        for parsed_module in parsed_modules:
            module = self.sync_parsed_module(parsed_module=parsed_module)
            modules.append(module)
        for module in modules:
            self.resolve_reference(module)
        return self.sync_modules

    def sync_parsed_module(self, parsed_module: ParsedModule) -> Module:
        match parsed_module:
            case ParsedFileModule():
                module = self.parsed_file_module_to_file_module(parsed_module)
            case ParsedDirectoryModule():
                module = self.parsed_directory_module_to_directory_module(parsed_module)
            case _:
                raise ValueError(f"Unsupported parsed module type: {parsed_module}")
        self.registry.register(module)
        self.mark_for_sync(module)
        return module

    def parsed_directory_module_to_directory_module(
        self, parsed_directory_module: ParsedDirectoryModule
    ) -> DirectoryModule:
        module = self.registry.find_by_path(path=parsed_directory_module.import_path)
        if module is None:
            module_id = ModuleId.create()
            sub_module_ids = []
        else:
            if not isinstance(module, DirectoryModule):
                raise ValueError(f"Module {module} is not a DirectoryModule")
            module_id = module.id
            sub_module_ids = module.sub_module_ids
        public_component_ids = [
            ReferenceTarget(raw=c)
            for c in parsed_directory_module.public_component_names
        ]
        return DirectoryModule(
            id=module_id,
            name=parsed_directory_module.name,
            path=parsed_directory_module.import_path,
            public_component_ids=public_component_ids,
            sub_module_ids=sub_module_ids,
            dir_module_id=None,
        )

    def parsed_file_module_to_file_module(
        self, parsed_file_module: ParsedFileModule
    ) -> FileModule:
        module = self.registry.find_by_path(path=parsed_file_module.import_path)
        if module is None:
            module_id = ModuleId.create()
            module_components = []
            dir_module_id = None
        else:
            if not isinstance(module, FileModule):
                raise ValueError(f"Module {module} is not a FileModule")
            module_id = module.id
            module_components = module.components
            dir_module_id = module.dir_module_id
        component_registry = ComponentRegistry(initial_components=module_components)
        sync_module_context = SyncModuleContext(
            module_id=module_id,
            module=parsed_file_module,
            component_registry=component_registry,
            path_parser=self.path_parser,
        )
        components = [
            sync_module_context.parsed_component_to_component(c)
            for c in parsed_file_module.components
        ]
        module_dependencies: list[ModuleDependency] = []
        for import_dto in parsed_file_module.dependencies:
            module_dependencies.extend(
                self.import_dto_to_module_dependencies(
                    import_dto=import_dto, parsed_file_module=parsed_file_module
                )
            )
        return FileModule(
            id=module_id,
            name=parsed_file_module.name,
            path=parsed_file_module.import_path,
            components=components,
            dependencies=module_dependencies,
            dir_module_id=dir_module_id,
        )

    def import_dto_to_module_dependencies(
        self, import_dto: ImportDto, parsed_file_module: ParsedFileModule
    ) -> list[ModuleDependency]:
        module_path = import_dto.resolve_module_path(
            current_file_dir=parsed_file_module.path
        )
        dependencies: list[ModuleDependency] = []
        for name in import_dto.names:
            module_dependency = ModuleDependency(
                module=ReferenceTarget(raw=module_path),
                component=ReferenceTarget(raw=name),
                type_checking=import_dto.type_checking,
            )
            dependencies.append(module_dependency)
        if not dependencies:
            dependencies.append(
                ModuleDependency(
                    module=ReferenceTarget(raw=module_path),
                    component=None,
                    type_checking=import_dto.type_checking,
                )
            )
        return dependencies

    def resolve_reference(self, module: Module) -> None:
        match module:
            case FileModule():
                self.resolve_file_module_reference(module)
            case DirectoryModule():
                self.resolve_directory_module_reference(module)
            case _:
                raise ValueError(f"Unsupported module type: {module}")

    def resolve_directory_module_reference(
        self, directory_module: DirectoryModule
    ) -> None:
        references = self.get_public_component_reference_targets(directory_module)
        directory_module.resolve(references)

    def get_public_component_reference_targets(
        self, directory_module: DirectoryModule
    ) -> dict[str, ReferenceTarget]:
        reference_map: dict[str, ReferenceTarget] = {}
        for module_id in directory_module.sub_module_ids:
            module = self.registry.find_by_id(module_id)
            if module is None:
                continue
            match module:
                case FileModule():
                    reference_map.update(self.get_component_references(module))
                case DirectoryModule():
                    reference_map.update(
                        self.get_public_component_reference_targets(module)
                    )
                case ExternalModule():
                    raise ValueError(f"External module is not supported: {module}")
        return reference_map

    def resolve_file_module_reference(self, file_module: FileModule) -> None:
        reference_map: dict[str, ReferenceTarget] = {}
        for component in file_module.components:
            reference_map[component.name] = ReferenceTarget(component_id=component.id)
        for dependency in file_module.dependencies:
            rm = self.get_dependency_references(dependency)
            reference_map.update(rm)
        file_module.resolve(reference_map)

    def get_dependency_references(
        self, dependency: ModuleDependency
    ) -> dict[str, ReferenceTarget]:
        reference_map: dict[str, ReferenceTarget] = {}
        module_path = dependency.module.raw
        if module_path is None:
            return reference_map
        module = self.find_module(path=module_path)
        if module is None:
            return reference_map
        reference_map[module_path] = ReferenceTarget(module_id=module.id)
        if dependency.component is None:
            return reference_map
        component_name = dependency.component.raw
        if component_name is None:
            return reference_map
        component = self.find_component(module=module, component_name=component_name)
        if component is None:
            return reference_map
        reference_map[component_name] = ReferenceTarget(component_id=component.id)
        return reference_map

    def find_module(self, path: str) -> Module | None:
        module = self.registry.find_by_path(path)
        return module

    def find_component(self, module: Module, component_name: str) -> Component | None:
        if isinstance(module, DirectoryModule):
            return None
        component = module.find_component(component_name)
        return component

    def get_component_references(
        self, module: FileModule, component_names: list[str] | None = None
    ) -> dict[str, ReferenceTarget]:
        reference_map: dict[str, ReferenceTarget] = {}
        for component in module.components:
            if component_names is not None and component.name not in component_names:
                continue
            reference_map[component.name] = ReferenceTarget(component_id=component.id)
        return reference_map
