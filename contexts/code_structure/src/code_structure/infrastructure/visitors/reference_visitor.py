from dataclasses import dataclass, field
from typing import override

from code_dom.domain.services.ast_visitor import AstVisitor
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from foundation.common_types.fqns.fqn import SymbolFqn


@dataclass
class ReferenceVisitor(AstVisitor):
    scope_symbols: dict[str, SymbolFqn]
    references: list[SymbolFqn] = field(default_factory=list, init=False)

    def __post_init__(self):
        super().__init__()
        self.references = []

    @override
    def visit_ast_name(self, node: AstName):
        if resolved_fqn := self.scope_symbols.get(node.id):
            if resolved_fqn not in self.references:
                self.references.append(resolved_fqn)


class FunctionVisitor(ReferenceVisitor):
    pass


class VariableVisitor(ReferenceVisitor):
    pass
