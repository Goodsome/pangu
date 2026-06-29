from abc import ABC
from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import ClassId
from foundation.persistence.ports.repository import Repository


class ClassRepository(Repository[ClassSymbol, ClassId], ABC):
    ...