from collections import defaultdict
from typing import Any, LiteralString, cast

from neo4j import GraphDatabase, Driver
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from codegen.shared.config import Settings
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)

# 导入现有的 SQLAlchemy 模型


def migrate_pg_to_memgraph(
    pg_uri: str, memgraph_uri: str = "bolt://localhost:7687"
) -> None:
    engine = create_engine(pg_uri)
    driver: Driver = GraphDatabase.driver(memgraph_uri, auth=None)

    with Session(engine) as session, driver.session() as mg_session:
        # ==========================================
        # 第一阶段：迁移节点
        # ==========================================
        nodes = session.scalars(select(CodeNodeModel)).all()
        nodes_by_kind: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

        for node in nodes:
            # 合并基础字段与 JSONB properties
            props = {
                "id": str(node.id),
                "fqn": node.fqn,
                "name": node.name,
                "description": node.description,
                "last_sync_id": node.last_sync_id,
                **node.properties,
            }
            # 清理 None 值（图数据库不支持 null 属性值）
            props = {k: v for k, v in props.items() if v is not None}
            nodes_by_kind[node.kind].append(props)

        for kind, batch in nodes_by_kind.items():
            label = kind.upper()

            # 创建节点
            query = f"""
            UNWIND $batch AS node
            MERGE (n:{label} {{id: node.id}})
            SET n += node
            """
            mg_session.run(cast(LiteralString, query), batch=batch)

            # 为当前 Label 的 id 字段创建索引，极大加速后续边的插入
            # Memgraph 索引语法支持对特定 Label 的属性建索引
            mg_session.run(cast(LiteralString, f"CREATE INDEX ON :{label}(id);"))

        # ==========================================
        # 第二阶段：迁移边
        # ==========================================
        edges = session.scalars(select(CodeEdgeModel)).all()
        edges_by_type: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

        for edge in edges:
            props = {"position": edge.position, **edge.properties}
            props = {k: v for k, v in props.items() if v is not None}
            edges_by_type[edge.type].append(
                {
                    "source_id": str(edge.source_id),
                    "target_id": str(edge.target_id),
                    "props": props,
                }
            )

        for edge_type, batch in edges_by_type.items():
            rel_type = edge_type.upper()

            # 根据 source_id 和 target_id 匹配节点并创建关系
            query = f"""
            UNWIND $batch AS edge
            MATCH (source {{id: edge.source_id}})
            MATCH (target {{id: edge.target_id}})
            MERGE (source)-[r:{rel_type}]->(target)
            SET r += edge.props
            """
            mg_session.run(cast(LiteralString, query), batch=batch)

    driver.close()


if __name__ == "__main__":
    settings = Settings()
    db_url = str(settings.database_url)
    migrate_pg_to_memgraph(pg_uri=db_url)
