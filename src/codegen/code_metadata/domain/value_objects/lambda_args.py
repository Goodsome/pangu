from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.value_objects.arg import Arg


@dataclass
class LambdaArgs:
    """Represents the parameter specification of a lambda (mirrors ast.arguments)."""

    posonlyargs: list[Arg] = field(default_factory=list)
    args: list[Arg] = field(default_factory=list)
    vararg: Arg | None = None
    kwonlyargs: list[Arg] = field(default_factory=list)
    kw_defaults: list[str | None] = field(default_factory=list)
    kwarg: Arg | None = None
    defaults: list[str | None] = field(default_factory=list)
