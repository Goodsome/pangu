from abc import ABC
from codegen.code_dom.domain.aggregates.codebase import Codebase
from codegen.shared.domain.ports.repository import Repository


class CodebaseRepository(Repository[Codebase, str], ABC):
    ...