from abc import ABC
from abc import abstractmethod
from collections.abc import Collection
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.domain.ports.repository import Repository


class CodeNodeRepository(Repository[CodeNode, Fqn], ABC):

    @abstractmethod
    def find_empty_modules(
        self, fqns: Collection[Fqn] | None = None
    ) -> list[CodeNode]: ...

    @abstractmethod
    def find_unused_nodes(
        self, kind: CodeNodeKind | None = None, fqns: Collection[str] | None = None
    ) -> list[CodeNode]: ...
