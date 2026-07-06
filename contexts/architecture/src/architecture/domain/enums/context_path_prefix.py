from enum import StrEnum


class ContextPathPrefix(StrEnum):
    CODEGEN = "src"
    
    FOUNDATION = "foundation/src"
    
    SPIKE = "contexts/spike/src"
    ARCHITECTURE = "contexts/architecture/src"
    CODE_DOM = "contexts/code_dom/src"
    CODE_STRUCTURE = "contexts/code_structure/src"
    
    PANGU_CLI = "apps/pangu_cli/src"
    PANGU_MCP = "apps/pangu_mcp/src"
    