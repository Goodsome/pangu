from dataclasses import dataclass
from architecture.domain.aggregates.base_module import BaseModule
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.services.file_module_registry import FileModuleRegistry
from architecture.domain.services.package_module_registry import PackageModuleRegistry
from foundation.common_types.context_name import ContextName
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.domain.value_objects.parsed_module import ParsedModule


@dataclass
class SyncModuleService:
    file_registry: FileModuleRegistry
    package_registry: PackageModuleRegistry

    def _resolve_id(self, fqn: ModuleFqn) -> ModuleId:
        """跨 registry 解析 fqn -> id"""
        file_mod = self.file_registry.find_by_fqn(fqn)
        if file_mod is not None:
            return file_mod.id
        pkg = self.package_registry.find_by_fqn(fqn)
        if pkg is not None:
            return pkg.id
        raise ValueError(f"Module with FQN {fqn} not found in any registry")

    def _ensure_or_delete(self, parsed_module: ParsedModule) -> None:
        fqn = parsed_module.fqn
        if parsed_module.is_package:
            if parsed_module.is_deleted:
                self.package_registry.delete_by_fqn(fqn)
            else:
                self.package_registry.ensure_package(fqn)
        else:
            if parsed_module.is_deleted:
                self.file_registry.delete_by_fqn(fqn)
            else:
                module = self.file_registry.ensure_file_module(fqn)
                parent = self.package_registry.ensure_package(fqn.parent_fqn)
                parent.add_contains(module.id)

    def _sync_dependencies(self, parsed_module: ParsedModule) -> None:
        fqn = parsed_module.fqn
        if parsed_module.is_package:
            module = self.package_registry.get_by_fqn(fqn)
        else:
            module = self.file_registry.get_by_fqn(fqn)
        dependencies: set[ModuleId] = set()
        for import_str in parsed_module.import_module_fqns:
            target_fqn = import_str
            if target_fqn.context not in ContextName._value2member_map_:
                continue
            dependencies.add(self._resolve_id(target_fqn))
        synced = module.sync_dependencies(dependencies)
        if synced:
            if isinstance(module, PackageModule):
                self.package_registry.mark_dirty(module)
            else:
                self.file_registry.mark_dirty(module)

    def sync_from_parsed_modules(
        self, parsed_modules: list[ParsedModule]
    ) -> list[BaseModule]:
        for parsed_module in parsed_modules:
            self._ensure_or_delete(parsed_module)

        for parsed_module in parsed_modules:
            if parsed_module.is_deleted:
                continue
            self._sync_dependencies(parsed_module)

        result: list[BaseModule] = []
        result.extend(self.file_registry.dirty_modules)
        result.extend(self.package_registry.dirty_modules)
        return result
