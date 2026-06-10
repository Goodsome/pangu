import ast
import difflib
from dataclasses import dataclass
from pathlib import Path
from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.code_metadata.domain.aggregates.module import FileModule
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.ports.module_repository import ModuleRepository
from codegen.code_metadata.domain.registries.component_registry import ComponentRegistry
from codegen.code_metadata.domain.registries.module_registry import ModuleRegistry
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.domain.services.translate_reference import TranslateReference
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class DevProgressService:
    file_system_port: FileSystemPort
    generator: CodeGenerator
    uow: UnitOfWork[ModuleRepository]
    path_parser: PathParser

    def get_dev_progress_v2(self, module_path: str | None = None) -> DevProgress:
        module_filter = ModuleFilter(kind=ModuleKind.FILE, path=module_path)
        modules, dependency_modules, dependency_components = self._get_modules(
            module_filter
        )
        file_metrics = [
            self._get_module_metric(module, dependency_modules, dependency_components)
            for module in modules
            if isinstance(module, FileModule)
        ]
        return DevProgress(records=file_metrics)

    def _get_modules(
        self, module_filter: ModuleFilter
    ) -> tuple[list[Module], dict[ModuleId, Module], dict[ComponentId, Component]]:
        with self.uow:
            modules = self.uow.repository.find_by_filter(module_filter)
            dependency_module_ids: set[ModuleId] = set()
            dependency_component_ids: set[ComponentId] = set()
            for module in modules:
                dependency_module_ids.update(module.get_dependency_modules())
                dependency_component_ids.update(module.get_dependency_components())
            dependency_modules = self.uow.repository.find_by_ids(
                list(dependency_module_ids)
            )
            dependency_components = self.uow.repository.find_components_by_ids(
                component_ids=list(dependency_component_ids)
            )
        return (modules, dependency_modules, dependency_components)

    def _get_module_metric(
        self,
        module: FileModule,
        dependency_modules: dict[ModuleId, Module],
        dependency_components: dict[ComponentId, Component],
    ) -> FileMetrics:
        parsed_path = self.path_parser.parse_module_path(module.path)
        module_code = self._generate_module_code(
            module, dependency_modules, dependency_components
        )
        origin_code = self._get_origin_code(module)
        ast_similarity = self.calculate_ast_similarity(module_code, origin_code)
        return FileMetrics(
            file_name=module.name,
            component_type=parsed_path.component_type,
            ast_similarity=ast_similarity,
            original_lines=len(origin_code.splitlines()),
            generated_lines=len(module_code.splitlines()),
            original_code=origin_code,
            generated_code=module_code,
        )

    def _generate_module_code(
        self,
        module: FileModule,
        dependency_modules: dict[ModuleId, Module],
        dependency_components: dict[ComponentId, Component],
    ) -> str:
        modules = [module] + [
            dependency_modules[module_id]
            for module_id in module.get_dependency_modules()
        ]
        module_registry = ModuleRegistry(init_modules=modules)
        components = module.components + [
            dependency_components[component_id]
            for component_id in module.get_dependency_components()
        ]
        component_registry = ComponentRegistry(initial_components=components)
        resolver = TranslateReference(
            id_map=component_registry._store_by_id,
            module_registry=module_registry,
            component_registry=component_registry,
        )
        module_code = self.generator.generate_module_code(
            module=module, resolver=resolver
        )
        return module_code

    def _get_origin_code(self, module: FileModule) -> str:
        file_path = Path("src") / module.path.replace(".", "/")
        file_path = file_path.with_suffix(".py")
        if not self.file_system_port.exists(file_path):
            return ""
        origin_code = self.file_system_port.read_file(file_path)
        return origin_code

    def calculate_ast_similarity(
        self, original_code: str, generated_code: str
    ) -> float:
        tree_orig = ast.parse(original_code)
        tree_gen = ast.parse(generated_code)
        tree_orig.body = [
            i for i in tree_orig.body if not isinstance(i, ast.ImportFrom)
        ]
        tree_gen.body = [i for i in tree_gen.body if not isinstance(i, ast.ImportFrom)]
        dump_orig = ast.dump(tree_orig, annotate_fields=True, include_attributes=False)
        dump_gen = ast.dump(tree_gen, annotate_fields=True, include_attributes=False)
        matcher = difflib.SequenceMatcher(
            None,
            dump_orig.replace("(", "\n").splitlines(),
            dump_gen.replace("(", "\n").splitlines(),
        )
        return matcher.ratio()
