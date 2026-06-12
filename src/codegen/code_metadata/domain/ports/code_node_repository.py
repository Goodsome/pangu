from abc import ABC
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.shared.domain.ports.repository import Repository


class CodeNodeRepository(Repository[CodeNode, Fqn], ABC):
    pass