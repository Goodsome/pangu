from code_structure.infrastructure.orm_models.symbol_node import SymbolNode


class ExternalSymbolNode(SymbolNode):
    name: str
    fqn: str
