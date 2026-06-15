from collections.abc import Collection
from dataclasses import dataclass
from typing import override
from uuid import UUID

from sqlalchemy import ColumnElement, exists, not_, or_, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from codegen.code_metadata.application.dtos.code_node_detail_dto import (
    CodeNodeDetailDto,
)
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.dispatcher import (
    orm_to_detail_dto,
    orm_to_dto,
)
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
    MethodNodeModel,
)


@dataclass
class SqlAlchemyCodeNodeQueryService(CodeNodeQueryService):
    session_factory: sessionmaker[Session]

    @override
    def find_by_fqn_prefix(self, fqn_prefix: str) -> list[CodeNode]:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.fqn.like(f"{fqn_prefix}%"))
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()
        return [orm_to_dto(m) for m in models]
        
    @override
    def find_by_fqn_prefixs(self, fqn_prefixs: Collection[str]) -> list[CodeNode]:
        
        conditions = [CodeNodeModel.fqn.startswith(p) for p in fqn_prefixs]
        stmt = (
            select(CodeNodeModel)
            .where(or_(*conditions))
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()
        return [orm_to_dto(m) for m in models]

    @override
    def find_by_fqns(
        self, fqns: Collection[str], with_outbounds: bool = False
    ) -> list[CodeNode]:
        if not fqns:
            return []
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.fqn.in_(fqns))
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()
        if not with_outbounds:
            return [orm_to_dto(m) for m in models]
        result_by_fqn: dict[str, CodeNodeModel] = {m.fqn: m for m in models}
        extra_fqns: set[str] = set()
        for m in models:
            for edge in m.outbound_edges:
                target = edge.target_entity
                if target is not None and target.fqn not in result_by_fqn:
                    extra_fqns.add(target.fqn)
        if extra_fqns:
            extra_stmt = (
                select(CodeNodeModel)
                .where(CodeNodeModel.fqn.in_(extra_fqns))
                .options(
                    selectinload(CodeNodeModel.outbound_edges).joinedload(
                        CodeEdgeModel.target_entity
                    )
                )
            )
            with self.session_factory() as session:
                extra_models = session.execute(extra_stmt).scalars().unique().all()
            result_by_fqn.update({m.fqn: m for m in extra_models})
        return [orm_to_dto(m) for m in result_by_fqn.values()]

    @override
    def find_by_fqn(self, fqn: str) -> CodeNodeDetailDto | None:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.fqn == fqn)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                ),
                selectinload(CodeNodeModel.inbound_edges).joinedload(
                    CodeEdgeModel.source_entity
                ),
            )
        )
        with self.session_factory() as session:
            model = session.execute(stmt).scalars().unique().one_or_none()
        if model is None:
            return None
        return orm_to_detail_dto(model)

    @override
    def find_by_id(self, node_id: UUID) -> CodeNodeDetailDto | None:
        stmt = (
            select(CodeNodeModel)
            .where(CodeNodeModel.id == node_id)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                ),
                selectinload(CodeNodeModel.inbound_edges).joinedload(
                    CodeEdgeModel.source_entity
                ),
            )
        )
        with self.session_factory() as session:
            model = session.execute(stmt).scalars().unique().one_or_none()
        if model is None:
            return None
        return orm_to_detail_dto(model)

    @override
    def find_unused_nodes(
        self,
        kind: CodeNodeKind | None = None,
        fqns: Collection[str] | None = None,
    ) -> list[CodeNode]:
        _SUPPORTED = {
            CodeNodeKind.CLASS,
            CodeNodeKind.FUNCTION,
            CodeNodeKind.VARIABLE,
        }
        _USAGE_EDGE_TYPES = {
            EdgeType.IMPORTS,
            EdgeType.INHERITS,
            EdgeType.CALLS,
            EdgeType.RETURNS,
            EdgeType.ACCEPTS,
            EdgeType.TYPED_AS,
            EdgeType.OVERRIDDES,
        }
        has_usage_inbound = exists().where(
            CodeEdgeModel.target_id == CodeNodeModel.id,
            CodeEdgeModel.type.in_(_USAGE_EDGE_TYPES),
        )
        conditions: list[ColumnElement[bool]] = [
            not_(has_usage_inbound),
            not_(CodeNodeModel.fqn.startswith("apps"))
        ]
        if kind:
            conditions.append(CodeNodeModel.kind == kind)
            if kind == CodeNodeKind.METHOD:
                conditions.append(MethodNodeModel.check_reachable.is_(True))
        else:
            conditions.append(CodeNodeModel.kind.in_(_SUPPORTED))
        if fqns:
            conditions.append(CodeNodeModel.fqn.in_(fqns))

        stmt = (
            select(CodeNodeModel)
            .where(*conditions)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()
        return [orm_to_dto(m) for m in models]

    @override
    def find_empty_modules(
        self,
        fqns: Collection[Fqn] | None = None,
    ) -> list[CodeNode]:
        has_defines_outbound = exists().where(
            CodeEdgeModel.source_id == CodeNodeModel.id,
            CodeEdgeModel.type.in_((EdgeType.DEFINES, EdgeType.CONTAINS)),
        )
        conditions: list[ColumnElement[bool]] = [
            CodeNodeModel.kind == CodeNodeKind.MODULE,
            not_(has_defines_outbound),
        ]
        if fqns:
            conditions.append(CodeNodeModel.fqn.in_(fqns))

        stmt = (
            select(CodeNodeModel)
            .where(*conditions)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()
        return [orm_to_dto(m) for m in models]

    @override
    def find_all_dead_nodes_cascading(
        self,
        kind: CodeNodeKind,
    ) -> list[CodeNode]:
        """
        通过单条 SQL (Recursive CTE) 找出所有死节点，包含级联变成死代码的节点。
        """
        _USAGE_EDGE_TYPES = {
            EdgeType.IMPORTS,
            EdgeType.INHERITS,
            EdgeType.CALLS,
            EdgeType.RETURNS,
            EdgeType.ACCEPTS,
            EdgeType.TYPED_AS,
        }

        # 1. Base Case: 选出确定的起点（活着的节点）
        base_stmt = select(CodeNodeModel.id).where(
            or_(
                CodeNodeModel.fqn.like("codegen.bootstrap%"),
                CodeNodeModel.fqn.like("%interface%"),
            )
        )

        # 将基础集声明为递归 CTE
        alive_cte = base_stmt.cte(name="alive_nodes", recursive=True)

        # 2. Recursive Step: 找出所有被存活节点连接的目标节点
        # 这里联表查找: CodeEdgeModel.source_id 是存活的 -> target_id 也是存活的
        recursive_stmt = (
            select(CodeEdgeModel.target_id)
            .join(alive_cte, alive_cte.c.id == CodeEdgeModel.source_id)
            .where(CodeEdgeModel.type.in_(_USAGE_EDGE_TYPES))
        )

        # 将基础集和递归集联合起来
        alive_cte = alive_cte.union_all(recursive_stmt)

        # 3. 主查询: 查出所有不在 "存活列表" 中的节点，即为全部的（包含级联的）死节点
        stmt = (
            select(CodeNodeModel)
            .where(
                CodeNodeModel.id.not_in(select(alive_cte.c.id)),
                CodeNodeModel.kind == kind,
            )
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )

        with self.session_factory() as session:
            models = session.execute(stmt).scalars().unique().all()

        return [orm_to_dto(m) for m in models]
