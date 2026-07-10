from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.building_blocks.command import Command


class RenameModuleCommand(Command):
    module_fqn: ModuleFqn
    new_name: str


@dataclass
class RenameModuleHandler:
    def execute(self, cmd: RenameModuleCommand, uow: UnitOfWork):
        module = uow.repository.find_by_fqn(cmd.module_fqn)
        if module is None:
            raise ValueError(f"Module not found: {cmd.module_fqn}")
        old_fqn = module.fqn
        if old_fqn.is_root:
            raise ValueError("Cannot rename root module")
        parent_fqn = old_fqn.parent_fqn
        new_fqn = ModuleFqn(f"{parent_fqn}.{cmd.new_name}")
        target_module = uow.repository.find_by_fqn(new_fqn)
        if target_module is not None:
            raise ValueError(f"Module already exists: {new_fqn}")

        module.moved(new_fqn)
        uow.repository.save(module)
