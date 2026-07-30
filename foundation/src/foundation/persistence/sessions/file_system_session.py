from typing import override
from foundation.persistence.ports.base_session import BaseSession


class FileSystemSession(BaseSession):
    """File System 暂未实现 Session/事务，提供 NoOp 基础会话以保持类型一致与向后兼容"""

    @override
    def commit(self) -> None:
        pass

    @override
    def rollback(self) -> None:
        pass

    @override
    def close(self) -> None:
        pass
