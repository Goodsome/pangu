
from pathlib import Path


class ContextRegistry:
    _contexts_cache: dict[str, Path] | None = None

    @classmethod
    def get_all_contexts(cls) -> dict[str, Path]:
        if cls._contexts_cache is not None:
            return cls._contexts_cache
            
        contexts: dict[str, Path] = {}
        if Path("foundation/src/foundation").exists():
            contexts["foundation"] = Path("foundation/src")
            
        for base_dir in ["apps", "contexts"]:
            base_path = Path(base_dir)
            if base_path.exists():
                for p in base_path.iterdir():
                    if p.is_dir() and (p / "src" / p.name).exists():
                        contexts[p.name] = p / "src"
        cls._contexts_cache = contexts
        return cls._contexts_cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._contexts_cache = None

    @classmethod
    def get_context_root_path(cls, context_name: str) -> Path:
        contexts = cls.get_all_contexts()
        if context_name in contexts:
            return contexts[context_name]
        return Path(f"contexts/{context_name}/src")

    @classmethod
    def resolve_context_name(cls, path: Path) -> str:
        for ctx_name, ctx_path in cls.get_all_contexts().items():
            if path.is_relative_to(ctx_path):
                return ctx_name
        raise ValueError(f"Path {path} does not belong to any supported context")

    @classmethod
    def get_relative_path(cls, path: Path) -> Path:
        for ctx_path in cls.get_all_contexts().values():
            if path.is_relative_to(ctx_path):
                return path.relative_to(ctx_path)
        raise ValueError(f"Path {path} does not belong to any supported context")

    @classmethod
    def check_path_in_contexts(cls, path: Path) -> bool:
        for ctx_path in cls.get_all_contexts().values():
            if path.is_relative_to(ctx_path):
                return True
        return False

    @classmethod
    def check_is_internal(cls, context_name: str) -> bool:
        return context_name in cls.get_all_contexts()
