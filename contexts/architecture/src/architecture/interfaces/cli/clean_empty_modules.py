from typing import Annotated
from dependency_injector.wiring import Provide, inject
from typer import Option
from architecture.application.commands.remove_module import RemoveModuleCommand
from architecture.application.ports.module_query_serivce import ModuleQueryService
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.infrastructure.message_bus import MessageBus


@inject
def _query_empty_packages(
    query_service: ModuleQueryService = Provide[
        "architecture_container.module_query_service"
    ],
) -> list[ModuleFqn]:
    empty_packages = query_service.find_empty_leaf_packages()
    unused_modules = query_service.find_unused_modules()
    return empty_packages + unused_modules


@inject
def _remove_module(
    cmd: RemoveModuleCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def clean_empty_modules(
    dry_run: Annotated[
        bool, Option("--dry-run", help="仅显示待删除的模块，不执行删除")
    ] = False,
) -> None:
    unused_modules = _query_empty_packages()
    if not unused_modules:
        print("No empty leaf packages found.")
        return
    if dry_run:
        print(f"Found {len(unused_modules)} unused module(s):")
        for fqn in unused_modules:
            print(f"  - {fqn}")
        return
    for fqn in unused_modules:
        _remove_module(RemoveModuleCommand(fqn=fqn))
    print(f"Deleted {len(unused_modules)} unused module(s).")
