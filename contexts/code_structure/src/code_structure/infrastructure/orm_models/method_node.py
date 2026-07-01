from code_structure.infrastructure.orm_models.symbol_node import SymbolNode


class MethodNode(SymbolNode):

    name: str
    fqn: str
