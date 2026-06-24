from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Set, List
from types import TracebackType
from typing_extensions import Self, override
import logging

logger = logging.getLogger(__name__)

# 占位类型，代表之前的领域模型
class CompilationUnit: pass
class FileMutation: pass

@dataclass
class WorkspaceSession:
    """
    等价于 SQLAlchemy 的 Session。
    纯内存操作，负责管理 AST 的 Identity Map 和状态追踪。
    """
    _identity_map: Dict[str, CompilationUnit] = field(default_factory=dict)
    _dirty_units: Set[CompilationUnit] = field(default_factory=set)
    _pending_mutations: List[FileMutation] = field(default_factory=list)

    def get_ast(self, file_path: str) -> CompilationUnit:
        # 从缓存或底层存储加载 AST
        pass

    def mark_dirty(self, unit: CompilationUnit) -> None:
        self._dirty_units.add(unit)

    def add_mutation(self, mutation: FileMutation) -> None:
        self._pending_mutations.append(mutation)

    def commit(self) -> None:
        """
        1. 计算 Diff
        2. 执行物理写入
        """
        # 1. 处方生成：计算内存中脏 AST 的文本 Diff
        for unit in self._dirty_units:
            # mutation = diff_engine.compute(unit)
            # self._pending_mutations.append(mutation)
            pass
            
        if not self._pending_mutations:
            return

        # 2. 抓药执行：交给文件系统执行原子写入
        # file_system_repo.apply(self._pending_mutations)
        logger.info(f"Committed {len(self._pending_mutations)} mutations to disk.")
        
        # 3. 清理状态
        self._dirty_units.clear()
        self._pending_mutations.clear()

    def rollback(self) -> None:
        """
        由于文件系统的特殊性，修改在 commit 之前都停留在内存中。
        因此，回滚通常只需要丢弃当前的内存状态即可，避免污染下一次操作。
        """
        self._dirty_units.clear()
        self._pending_mutations.clear()
        # 注意：如果 AST 对象本身被原地修改了（Mutable），回滚时还需要将 Identity Map 
        # 中的 AST 丢弃，强制下一次读取时重新从磁盘解析。
        self._identity_map.clear()
        logger.info("WorkspaceSession state rolled back.")

    def close(self) -> None:
        self.rollback()