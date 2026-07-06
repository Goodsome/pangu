from enum import StrEnum, auto


class ContextName(StrEnum):
    CODEGEN = auto()
    
    FOUNDATION = auto()

    SPIKE = auto()
    
    ARCHITECTURE = auto()
    CODE_DOM = auto()
    CODE_STRUCTURE = auto()
    
    PANGU_CLI = auto()
    PANGU_MCP = auto()