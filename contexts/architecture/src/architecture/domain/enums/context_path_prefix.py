from enum import StrEnum


class ContextPathPrefix(StrEnum):
    ARCHITECTURE = "contexts/architecture/src"
    CODE_DOM = "contexts/code_dom/src"
    CODE_STRUCTURE = "contexts/code_structure/src"
    CODEGEN = "src"
    PANGU_CLI = "apps/pangu_cli/src"
    FOUNDATION = "foundation/src"
    