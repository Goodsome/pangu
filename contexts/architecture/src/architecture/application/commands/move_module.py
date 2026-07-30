from dataclasses import dataclass
from architecture.application.ports.repo_provider import RepoProvider
from architecture.domain.aggregates.package_module import PackageModule
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.building_blocks.command import Command


class MoveModuleCommand(Command):
    module_fqn: ModuleFqn
    target_fqn: ModuleFqn


@dataclass
class MoveModuleHandler:
    def execute(self, cmd: MoveModuleCommand, uow: RepoProvider):
        module = uow.find_module_by_fqn(cmd.module_fqn)
        if module is None:
            raise ValueError(f"Module not found: {cmd.module_fqn}")
        target = uow.packages.find_by_fqn(cmd.target_fqn)
        if target is None:
            raise ValueError(f"Target package not found: {cmd.target_fqn}")
        old_fqn = module.fqn
        new_fqn = ModuleFqn(f"{target.fqn}.{old_fqn.symbol}")
        existing = uow.find_module_by_fqn(new_fqn)
        if existing is not None:
            raise ValueError(f"Module already exists: {new_fqn}")

        old_parent_fqn = old_fqn.parent_fqn
        old_parent = uow.packages.find_by_fqn(old_parent_fqn)
        if old_parent is not None:
            old_parent.remove_contains(module.id)
            uow.packages.save(old_parent)
        target.add_contains(module.id)
        module.moved(new_fqn)
        if isinstance(module, PackageModule):
            uow.packages.save(module)
        else:
            uow.file_modules.save(module)
        uow.packages.save(target)
