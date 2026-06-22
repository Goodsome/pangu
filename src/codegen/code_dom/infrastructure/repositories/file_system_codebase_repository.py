from typing import override
from codegen.code_dom.domain.aggregates.codebase import Codebase
from codegen.code_dom.domain.repositories.codebase_repository import CodebaseRepository
from codegen.shared.domain.ports.file_system_port import FileSystemPort


class FileSystemCodebaseRepository(CodebaseRepository):
    file_system: FileSystemPort

    @override
    def _add(self, aggregate: Codebase) -> None:
        raise NotImplementedError()

    @override
    def _add_all(self, aggregates: list[Codebase]) -> None:
        raise NotImplementedError()
    
    @override
    def _get(self, id: str) -> Codebase:
        codebase = Codebase(
            id=id,
        )
        return codebase

    @override
    def _save(self, aggregate: Codebase) -> None:
        raise NotImplementedError()
    
    @override
    def _delete(self, aggregate: Codebase) -> None:
        raise NotImplementedError()

    @override
    def _save_all(self, aggregates: list[Codebase]) -> None:
        raise NotImplementedError()
