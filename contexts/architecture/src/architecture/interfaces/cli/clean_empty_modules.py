from typing import Annotated

from dependency_injector.wiring import Provide, inject
from typer import Option

from architecture.application.commands.remove_module import RemoveModuleCommand
from architecture.application.ports.module_query_serivce import ModuleQueryService
from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.infrastructure.message_bus import MessageBus


@inject
def _query_empty_packages(
    query_service: ModuleQueryService = Provide["architecture_container.module_query_service"],
) -> list[ModuleFqn]:
    return [fqn for fqn in query_service.find_empty_leaf_packages()]


@inject
def _remove_module(
    cmd: RemoveModuleCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)

def clean_empty_modules(
    dry_run: Annotated[bool, Option("--dry-run", help="仅显示待删除的模块，不执行删除")] = False,
) -> None:
    empty_fqns = _query_empty_packages()
    if not empty_fqns:
        print("No empty leaf packages found.")
        return

    if dry_run:
        print(f"Found {len(empty_fqns)} empty leaf package(s):")
        for fqn in empty_fqns:
            print(f"  - {fqn}")
        return

    for fqn in empty_fqns:
        _remove_module(RemoveModuleCommand(fqn=fqn))

    print(f"Deleted {len(empty_fqns)} empty leaf package(s).")
