from dataclasses import dataclass
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.exceptions.father_module_not_exists import (
    FatherModuleNotExists,
)
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.building_blocks.command import Command


class CreatePackageCommand(Command):
    fqn: ModuleFqn


@dataclass
class CreatePackageHandler:
    def execute(self, cmd: CreatePackageCommand, uow: UnitOfWork):
        fqn = cmd.fqn
        if not fqn.is_root:
            parent_fqn = fqn.parent_fqn
            parent = uow.packages.find_by_fqn(parent_fqn)
            if parent is None:
                raise FatherModuleNotExists(fqn=fqn, parent_fqn=parent_fqn)
            module = PackageModule.create(fqn=fqn, name=fqn.symbol)
            uow.packages.save(module)
            parent.add_contains(module.id)
            uow.packages.save(parent)
        else:
            module = PackageModule.create(fqn=fqn, name=fqn.symbol)
            uow.packages.save(module)
