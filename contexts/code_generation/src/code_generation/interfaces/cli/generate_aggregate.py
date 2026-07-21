from typing import Annotated

from dependency_injector.wiring import Provide, inject
from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString
from typer import Argument

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


def generate_aggregate(
    context: Annotated[str, Argument(help="Context name (上下文名称)")],
    name: Annotated[str, Argument(help="Aggregate name (聚合名称)")],
) -> None:
    """Generate aggregate and identity classes (生成聚合和标识类)"""
    cmd = GenerateAggregateCommand(context=context, name=name)
    _generate_aggregate(cmd)
