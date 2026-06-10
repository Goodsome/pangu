from pathlib import Path
from pydantic import BaseModel
from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.services.path_parser import PathParser


class ImportDto(BaseModel):
    module: str | None
    level: int
    names: list[str]
    type_checking: bool = False

    def resolve_module_path(self, current_file_dir: Path) -> str:
        if self.level == 0:
            assert self.module is not None
            return self.module
        else:
            internal_path = self._resolve_internal_path(current_file_dir)
            return PathParser.normalize(internal_path)

    def resolve_module_kind(self, current_file_dir: Path) -> ModuleKind:
        src_root: Path = Path("src/")
        if self.level > 0:
            internal_path = self._resolve_internal_path(current_file_dir)
            if internal_path.with_suffix(".py").is_file():
                return ModuleKind.FILE
            else:
                return ModuleKind.DIRECTORY
        if self.module:
            module_path_parts = self.module.split(".")
            potential_path = src_root / Path(*module_path_parts)
            if potential_path.with_suffix(".py").is_file():
                return ModuleKind.FILE
            if potential_path.is_dir():
                return ModuleKind.DIRECTORY
        return ModuleKind.EXTERNAL

    def _resolve_internal_path(self, current_file_dir: Path) -> Path:
        """辅助方法：解析相对导入的具体路径"""
        steps_up = self.level - 1
        target_dir = current_file_dir
        for _ in range(steps_up):
            target_dir = target_dir.parent
        if self.module:
            module_path_parts = self.module.split(".")
            target_path = target_dir / Path(*module_path_parts)
        else:
            target_path = target_dir
        return target_path
