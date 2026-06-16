from abc import ABC
from abc import abstractmethod
from collections.abc import Collection
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.domain.ports.repository import Repository


class CodeNodeRepository(Repository[CodeNode, Fqn], ABC):

    @abstractmethod
    def find_empty_modules(
        self, fqns: Collection[Fqn] | None = None
    ) -> list[CodeNode]: ...

    @abstractmethod
    def move_node(
        self, node_fqn: Fqn, target_fqn: Fqn
    ) -> Fqn: ...
    
    