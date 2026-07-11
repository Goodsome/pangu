from dataclasses import dataclass
from pathlib import Path
from foundation.common_types.context_name import ContextName
from architecture.domain.enums.context_path_prefix import ContextPathPrefix


@dataclass
class ContextRegistry:
    @staticmethod
    def get_context_root_path(context_name: ContextName) -> Path:
        return Path(ContextPathPrefix[context_name.name])

    @staticmethod
    def resolve_context_name(path: Path) -> ContextName:
        for path_prefix in ContextPathPrefix:
            if path.is_relative_to(Path(path_prefix)):
                return ContextName[path_prefix.name]
        raise ValueError(f"Path {path} does not belong to any supported context")

    @staticmethod
    def get_relative_path(path: Path) -> Path:
        for path_prefix in ContextPathPrefix:
            if path.is_relative_to(Path(path_prefix)):
                return path.relative_to(Path(path_prefix))
        raise ValueError(f"Path {path} does not belong to any supported context")

    @staticmethod
    def check_path_in_contexts(path: Path) -> bool:
        for path_prefix in ContextPathPrefix:
            if path.is_relative_to(Path(path_prefix)):
                return True
        return False