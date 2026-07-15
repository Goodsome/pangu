from dataclasses import dataclass

from code_generation.application.commands.generate_aggregate import (
    GenerateAggregateCommand,
    GenerateAggregateCommandHandler,
)


@dataclass
class CodeGenerationApi:
    generate_aggregate_handler: GenerateAggregateCommandHandler

    def generate_aggregate(self, context: str, name: str) -> None:
        cmd = GenerateAggregateCommand(context=context, name=name)
        self.generate_aggregate_handler.execute(cmd)
