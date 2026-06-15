from collections.abc import Collection
from dataclasses import dataclass
from typing import cast, override
from uuid import UUID

from sqlalchemy import delete, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session, sessionmaker

from codegen.code_metadata.application.dtos.bulk_save_result import BulkSaveResult
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.domain.aggregates.code_edge import CodeEdgeAggregate
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    code_edge_to_upsert_dict as edge_to_upsert_dict,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.dispatcher import (
    dto_to_upsert_dict,
)
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)


@dataclass
class SqlAlchemyCodeNodeSyncService(CodeNodeSyncService):
    """CodeNode 批量同步的 SQLAlchemy 实现。"""

    session_factory: sessionmaker[Session]

    @override
    def save_nodes_bulk(
        self,
        node_dtos: list[CodeNode],
        sync_id: str,
        fqn_prefix: str,
        code_edges: Collection[CodeEdgeAggregate],
    ) -> BulkSaveResult:
        if not node_dtos:
            return BulkSaveResult(nodes_upserted=0, edges_created=0)
        with self.session_factory() as session:
            node_values = [dto_to_upsert_dict(dto, sync_id) for dto in node_dtos]
            stmt = insert(CodeNodeModel)
            stmt = stmt.on_conflict_do_update(
                index_elements=["fqn"],
                set_={
                    "name": stmt.excluded.name,
                    "kind": stmt.excluded.kind,
                    "description": stmt.excluded.description,
                    "properties": stmt.excluded.properties,
                    "last_sync_id": stmt.excluded.last_sync_id,
                },
            )
            session.execute(stmt, node_values)
            external_fqns: set[str] = set()
            for dto in node_dtos:
                for edge in dto.outbound_edges:
                    if not edge.fqn.startswith(fqn_prefix):
                        external_fqns.add(edge.fqn)
                        
            for code_edge in code_edges:
                if not code_edge.source_id.startswith(fqn_prefix):
                    external_fqns.add(code_edge.source_id)
                if not code_edge.target_id.startswith(fqn_prefix):
                    external_fqns.add(code_edge.target_id)
                    
            conditions = [CodeNodeModel.fqn.startswith(fqn_prefix)]
            if external_fqns:
                conditions.append(CodeNodeModel.fqn.in_(external_fqns))
            rows = session.execute(
                select(CodeNodeModel.id, CodeNodeModel.fqn).where(or_(*conditions))
            ).all()
            fqn_to_id: dict[str, UUID] = {fqn: uid for uid, fqn in rows}
            subq = (
                select(CodeNodeModel.id)
                .where(CodeNodeModel.fqn.startswith(fqn_prefix))
                .scalar_subquery()
            )
            session.execute(
                delete(CodeEdgeModel).where(CodeEdgeModel.source_id.in_(subq))
            )
            edge_values: list[dict[str, object]] = []
            for dto in node_dtos:
                source_id = fqn_to_id.get(dto.id)
                if not source_id:
                    continue
                for idx, edge_dto in enumerate(dto.outbound_edges):
                    target_id = fqn_to_id.get(edge_dto.fqn)
                    if not target_id:
                        continue
                    edge_dict = edge_to_upsert_dict(edge_dto)
                    edge_dict["source_id"] = source_id
                    edge_dict["target_id"] = target_id
                    edge_dict["position"] = idx
                    edge_values.append(edge_dict)
            for code_edge in code_edges:
                source_id = fqn_to_id.get(code_edge.source_id)
                target_id = fqn_to_id.get(code_edge.target_id)
                if not source_id or not target_id:
                    continue
                edge_dict: dict[str, object] = {
                    "source_id": source_id,
                    "target_id": target_id,
                    "type": code_edge.edge_type,
                    "position": None,
                    "properties": {}
                }
                edge_values.append(edge_dict)
            if edge_values:
                insert_edge_stmt = insert(CodeEdgeModel)
                insert_edge_stmt = insert_edge_stmt.on_conflict_do_update(
                    constraint="uq_entity_edge",
                    set_={
                        "position": insert_edge_stmt.excluded.position, 
                        "properties": insert_edge_stmt.excluded.properties,
                    }
                )
                session.execute(insert_edge_stmt, edge_values)
            session.commit()
        return BulkSaveResult(
            nodes_upserted=len(node_values), edges_created=len(edge_values)
        )

    @override
    def delete_stale_nodes(self, fqn_prefix: str, current_sync_id: str) -> int:
        with self.session_factory() as session:
            stmt = delete(CodeNodeModel).where(
                CodeNodeModel.fqn.startswith(fqn_prefix),
                CodeNodeModel.last_sync_id != current_sync_id,
            )
            result = session.execute(stmt)
            session.commit()
            return cast(CursorResult[int], result).rowcount
