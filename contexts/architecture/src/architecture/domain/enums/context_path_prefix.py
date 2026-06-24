from enum import StrEnum


class ContextPathPrefix(StrEnum):
    ARCHITECTURE = "contexts/architecture/src"
    CODE_DOM = "contexts/code_dom/src"
    CODEGEN = "src"
    PANGU_CLI = "apps/pangu_cli/src"
    FOUNDATION = "foundation/src"
    