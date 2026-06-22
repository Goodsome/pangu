from dataclasses import dataclass

from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.aggregates.module import Module
from architecture.domain.exceptions.father_module_not_exists import FatherModuleNotExists
from architecture.domain.value_objects.fqn import ModuleFqn
from foundation.building_blocks.command import Command


class CreatePackageCommand(Command):
    fqn: ModuleFqn


@dataclass
class CreatePackageHandler:
    def execute(self, cmd: CreatePackageCommand, uow: UnitOfWork):
        fqn = cmd.fqn

        if not fqn.is_root:
            parent_fqn = fqn.parent_fqn
            parent = uow.repository.find_by_fqn(parent_fqn)
            if parent is None:
                raise FatherModuleNotExists(fqn=fqn, parent_fqn=parent_fqn)
            module = Module.create(
                fqn=fqn, name=fqn.symbol, is_package=True
            )
            uow.repository.save(module)
            parent.add_contains(module.id)
            uow.repository.save(parent)
        else:
            module = Module.create(
                fqn=fqn, name=fqn.symbol, is_package=True
            )
            uow.repository.save(module)
