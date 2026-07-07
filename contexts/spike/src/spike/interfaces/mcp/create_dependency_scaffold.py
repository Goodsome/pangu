from dependency_injector.wiring import Provide, inject

from spike.application.commands.create_dependency_scaffold import (
    CreateDependencyScaffoldCommand,
    CreateDependencyScaffoldCommandHandler,
    CreateDependencyScaffoldResult,
)
from spike.domain.value_objects.scaffold_payload import ScaffoldPayload


@inject
async def _create_dependency_scaffold(
    cmd: CreateDependencyScaffoldCommand,
    handler: CreateDependencyScaffoldCommandHandler = Provide[
        "spike_container.create_dependency_scaffold_handler"
    ],
) -> CreateDependencyScaffoldResult:
    return await handler.execute(cmd)


async def create_dependency_scaffold(
    payload: ScaffoldPayload,
) -> CreateDependencyScaffoldResult:
    cmd = CreateDependencyScaffoldCommand(scaffold_payload=payload)
    return await _create_dependency_scaffold(cmd)
