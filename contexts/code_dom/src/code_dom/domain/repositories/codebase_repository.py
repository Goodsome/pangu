from abc import ABC
from code_dom.domain.aggregates.codebase import Codebase
from foundation.persistence.ports.repository import Repository


class CodebaseRepository(Repository[Codebase, str], ABC): ...
