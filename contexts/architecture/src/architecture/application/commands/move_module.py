from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.building_blocks.command import Command


class MoveModuleCommand(Command):
    module_fqn: ModuleFqn
    target_fqn: ModuleFqn


@dataclass
class MoveModuleHandler:
    def execute(self, cmd: MoveModuleCommand, uow: UnitOfWork):
        module = uow.repository.find_by_fqn(cmd.module_fqn)
        if module is None:
            raise ValueError(f"Module not found: {cmd.module_fqn}")
        target = uow.repository.find_by_fqn(cmd.target_fqn)
        if target is None:
            raise ValueError(f"Target module not found: {cmd.target_fqn}")
        old_fqn = module.fqn
        new_fqn = ModuleFqn(f"{target.fqn}.{old_fqn.symbol}")
        new_module = uow.repository.find_by_fqn(new_fqn)
        if new_module is not None:
            raise ValueError(f"Module already exists: {new_fqn}")
        
        old_parent_fqn = old_fqn.parent_fqn
        old_parent = uow.repository.find_by_fqn(old_parent_fqn)
        if old_parent is not None:
            old_parent.remove_contains(module.id)
            uow.repository.save(old_parent)
        target.add_contains(module.id)
        module.moved(new_fqn)
        uow.repository.save(target)
        uow.repository.save(module)
