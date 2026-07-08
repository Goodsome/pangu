from dataclasses import dataclass, field
from typing import override

from code_dom.domain.services.ast_visitor import AstVisitor
from code_structure.domain.value_objects.parsed_reference import ParsedReference
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from foundation.common_types.fqns.fqn import SymbolFqn


@dataclass
class ReferenceVisitor(AstVisitor):
    scope_symbols: dict[str, SymbolFqn]
    references: list[ParsedReference] = field(default_factory=list, init=False)

    def __post_init__(self):
        super().__init__()
        self.references = []

    @override
    def visit_ast_name(self, node: AstName):
        if resolved_fqn := self.scope_symbols.get(node.id):
            alias = node.id if node.id != resolved_fqn.symbol else None
            if not any(r.target_fqn == resolved_fqn for r in self.references):
                self.references.append(
                    ParsedReference(target_fqn=resolved_fqn, alias=alias)
                )


class FunctionVisitor(ReferenceVisitor):
    pass


class VariableVisitor(ReferenceVisitor):
    pass
