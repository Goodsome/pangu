import logging
import json
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Protocol, override, Self

from neo4j import Driver, Session, Transaction

from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.core.event import IntegrationEvent
from codegen.shared.domain.ports.repository import Repository

logger = logging.getLogger(__name__)


class RepositoryFactory[T: Repository[Any, Any]](Protocol):

    def __call__(self, transaction: Transaction) -> T:
        ...

@dataclass
class MemgraphUnitOfWork[T_Repo: Repository[Any, Any]](UnitOfWork[T_Repo]):
    # 注入 neo4j.Driver 替代 sessionmaker
    driver: Driver
    repository_factory: RepositoryFactory[T_Repo]
    
    session: Session | None = field(default=None, init=False)
    transaction: Transaction | None = field(default=None, init=False)
    _repository: T_Repo | None = field(default=None, init=False)

    @override
    def __enter__(self) -> Self:
        self.session = self.driver.session()
        self.transaction = self.session.begin_transaction()
        
        # 将 transaction 对象传递给 Repository，Repository 需要使用 tx.run() 来执行 Cypher
        self._repository = self.repository_factory(self.transaction)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is not None:
            self.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            # 保持与原版行为一致，此处不主动 commit，由应用层显式调用 uow.commit()
            pass
            
        # 依次安全关闭事务和会话
        if self.transaction:
            self.transaction.close()
            self.transaction = None
            
        if self.session:
            self.session.close()
            self.session = None
            
        self._repository = None

    @property
    @override
    def repository(self) -> T_Repo:
        if not self._repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._repository

    @override
    def commit(self):
        if self.transaction:
            self.transaction.commit()

    @override
    def rollback(self):
        if self.transaction:
            self.transaction.rollback()

    @override
    def save_outbox_message(self, message: IntegrationEvent):
        if not self.transaction:
            raise RuntimeError("Transaction is not active")
            
        # neo4j 驱动传递字典/JSON 时，通常使用 JSON 字符串或者展开为节点属性
        payload = message.model_dump(mode="json")
        event_type = type(message).__name__
        
        # 使用 Cypher 语句持久化发件箱消息作为图节点
        query = """
        CREATE (o:OutboxMessage {
            event_type: $event_type,
            payload: $payload,
            created_at: timestamp()
        })
        """
        # 如果 payload 是复杂的嵌套字典，可能需要将其转换为字符串存储： json.dumps(payload)
        # Memgraph 支持直接存储字符串或基本类型的属性
        self.transaction.run(
            query, 
            event_type=event_type, 
            payload=json.dumps(payload)
        )