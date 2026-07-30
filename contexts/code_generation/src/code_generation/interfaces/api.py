from dataclasses import dataclass

from code_generation.application.commands.delete_aggregate import (
    DeleteAggregateCommand,
    DeleteAggregateCommandHandler,
)
from code_generation.application.commands.generate_aggregate import (
    GenerateAggregateCommand,
    GenerateAggregateCommandHandler,
)


@dataclass
class CodeGenerationApi:
    generate_aggregate_handler: GenerateAggregateCommandHandler
    delete_aggregate_handler: DeleteAggregateCommandHandler

    def generate_aggregate(
        self, context: str, name: str, is_async: bool = True
    ) -> None:
        cmd = GenerateAggregateCommand(context=context, name=name, is_async=is_async)
        self.generate_aggregate_handler.execute(cmd)

    def delete_aggregate(self, context: str, name: str, is_async: bool = True) -> None:
        cmd = DeleteAggregateCommand(context=context, name=name, is_async=is_async)
        self.delete_aggregate_handler.execute(cmd)
