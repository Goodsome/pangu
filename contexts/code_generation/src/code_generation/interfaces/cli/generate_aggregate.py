from typing import Annotated

from dependency_injector.wiring import Provide, inject
from typer import Argument, Option

from code_generation.application.commands.delete_aggregate import (
    DeleteAggregateCommand,
    DeleteAggregateCommandHandler,
)
from code_generation.application.commands.generate_aggregate import (
    GenerateAggregateCommand,
    GenerateAggregateCommandHandler,
)


@inject
def _generate_aggregate(
    cmd: GenerateAggregateCommand,
    handler: GenerateAggregateCommandHandler = Provide[
        "code_generation_container.generate_aggregate_handler"
    ],
) -> None:
    handler.execute(cmd)


@inject
def _delete_aggregate(
    cmd: DeleteAggregateCommand,
    handler: DeleteAggregateCommandHandler = Provide[
        "code_generation_container.delete_aggregate_handler"
    ],
) -> None:
    handler.execute(cmd)


def generate_aggregate(
    context: Annotated[str, Argument(help="Context name (上下文名称)")],
    name: Annotated[str, Argument(help="Aggregate name (聚合名称)")],
    rm: Annotated[
        bool,
        Option(
            "--rm",
            help="Remove/delete aggregate code files instead of generating (删除生成的聚合代码文件)",
        ),
    ] = False,
) -> None:
    """Generate or remove aggregate and identity classes (生成或删除聚合和标识类)"""
    if rm:
        delete_cmd = DeleteAggregateCommand(context=context, name=name)
        _delete_aggregate(delete_cmd)
    else:
        gen_cmd = GenerateAggregateCommand(context=context, name=name)
        _generate_aggregate(gen_cmd)
