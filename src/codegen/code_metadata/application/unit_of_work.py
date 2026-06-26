from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from foundation.persistence.ports.unit_of_work import UnitOfWork as BaseUnitOfWork

UnitOfWork = BaseUnitOfWork[CodeNodeRepository]
