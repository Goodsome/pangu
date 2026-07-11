from dataclasses import dataclass
from architecture.domain.aggregates.base_module import BaseModule
from foundation.common_types.context_name import ContextName
from foundation.common_types.identities.module_id import ModuleId
from architecture.domain.services.module_registry import ModuleRegistry
from architecture.domain.value_objects.parsed_module import ParsedModule


@dataclass
class SyncModuleService:
    module_registry: ModuleRegistry

    def sync_from_parsed_modules(
        self, parsed_modules: list[ParsedModule]
    ) -> list[BaseModule]:
        for parsed_module in parsed_modules:
            fqn = parsed_module.fqn
            is_package = parsed_module.is_package
            if parsed_module.is_deleted:
                self.module_registry.delete_by_fqn(fqn)
            else:
                self.module_registry.ensure_module(fqn, is_package)
        for parsed_module in parsed_modules:
            if parsed_module.is_deleted:
                continue
            fqn = parsed_module.fqn
            module = self.module_registry.get_by_fqn(fqn)
            dependencies: set[ModuleId] = set()
            for import_str in parsed_module.import_module_fqns:
                target_fqn = import_str
                if target_fqn.context not in ContextName._value2member_map_:
                    continue
                dependencies.add(self.module_registry.get_id_by_fqn(target_fqn))
            synced = module.sync_dependencies(dependencies)
            if synced:
                self.module_registry.mark_dirty(module)
        return list(self.module_registry.dirty_modules)
