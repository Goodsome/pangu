from codegen.shared.domain.core.command import Command


class GenerateCodeCommand(Command):
    fqns: list[str]
