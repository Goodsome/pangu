import time
from collections import defaultdict
from typing import Any
from uuid import uuid4

from neo4j import GraphDatabase, Driver
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from codegen.code_metadata.infrastructure.orm_models.code_edge_model import CodeEdgeModel
from codegen.code_metadata.infrastructure.orm_models.code_node_model import CodeNodeModel
from codegen.shared.config import Settings


def run_full_graph_sync(pg_uri: str, memgraph_uri: str = "bolt://localhost:7687") -> None:
    engine = create_engine(pg_uri)
    driver: Driver = GraphDatabase.driver(memgraph_uri, auth=None)
    
    # 1. 生成本次全量同步的唯一水位线标记
    current_sync_id = f"sync_{int(time.time())}_{uuid4().hex[:8]}"
    print(f"Starting full sync with ID: {current_sync_id}")

    with Session(engine) as session, driver.session() as mg_session:
        # ==========================================
        # 阶段一：全量同步节点（并打上 sync_id 水印）
        # ==========================================
        nodes = session.scalars(select(CodeNodeModel)).all()
        nodes_by_kind: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for node in nodes:
            props = {
                "id": str(node.id),
                "fqn": node.fqn,
                "name": node.name,
                "description": node.description,
                "last_sync_id": current_sync_id,  # 强制覆盖为本次的 Sync ID
                **node.properties
            }
            props = {k: v for k, v in props.items() if v is not None}
            nodes_by_kind[node.kind].append(props)

        for kind, batch in nodes_by_kind.items():
            label = kind.upper()
            query = f"""
            UNWIND $batch AS node
            MERGE (n:{label} {{fqn: node.fqn}}) // 使用 fqn 作为业务主键更稳妥
            SET n += node
            """
            mg_session.run(query, batch=batch)
            mg_session.run(f"CREATE INDEX ON :{label}(fqn);")
        print(f"✅ Synced {len(nodes)} nodes.")

        # ==========================================
        # 阶段二：全量同步关系（业务边）
        # ==========================================
        edges = session.scalars(select(CodeEdgeModel)).all()
        edges_by_type: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

        # 为了性能，直接在 PG 内存中建立 ID 到 FQN 的映射，避免图数据库中的跨度查询
        id_to_fqn = {str(n.id): n.fqn for n in nodes}

        for edge in edges:
            src_fqn = id_to_fqn.get(str(edge.source_id))
            tgt_fqn = id_to_fqn.get(str(edge.target_id))
            
            if not src_fqn or not tgt_fqn:
                continue
                
            props = {"position": edge.position, **edge.properties}
            props = {k: v for k, v in props.items() if v is not None}
            
            edges_by_type[edge.type].append({
                "source_fqn": src_fqn,
                "target_fqn": tgt_fqn,
                "props": props
            })

        mg_session.run("MATCH ()-[r]->() DELETE r")

        for edge_type, batch in edges_by_type.items():
            rel_type = edge_type.upper()
            query = f"""
            UNWIND $batch AS edge
            MATCH (source {{fqn: edge.source_fqn}})
            MATCH (target {{fqn: edge.target_fqn}})
            MERGE (source)-[r:{rel_type}]->(target)
            SET r += edge.props
            """
            mg_session.run(query, batch=batch)
        print(f"✅ Synced {len(edges)} edges.")

        # ==========================================
        # 阶段三：清理幽灵数据 (Garbage Collection)
        # ==========================================
        # 找出所有最后同步 ID 不是本次 ID 的节点，并连同它们的边一起干掉
        cleanup_query = """
        MATCH (n)
        WHERE n.last_sync_id <> $sync_id OR n.last_sync_id IS NULL
        WITH n DETACH DELETE n
        RETURN count(n) AS deleted_count
        """
        result = mg_session.run(cleanup_query, sync_id=current_sync_id)
        deleted_count = result.single()["deleted_count"]
        print(f"🗑️ Cleaned up {deleted_count} stale nodes.")

    driver.close()
    print("🎉 Full sync completed successfully.")

if __name__ == "__main__":
    settings = Settings()
    db_url = str(settings.database_url)
    run_full_graph_sync(pg_uri=db_url)