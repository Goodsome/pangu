from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, TypeVar

from neo4j import Driver, Result, Session, Transaction
from pydantic import BaseModel

from foundation.persistence.orm.neo4j_base import (
    EdgeModel,
    NodeModel,
    RelationDirection,
    RelationshipMeta,
)

TNode = TypeVar("TNode", bound=NodeModel)


@dataclass
class Neo4jSession:
    """
    轻量级的 Neo4j Unit of Work / Session。
    负责对象状态收集、Cypher 批处理转换、事务管理以及基于元数据的动态查询。
    """

    driver: Driver
    _session: Session = field(init=False)
    _transaction: Transaction = field(init=False)
    
    _pending_nodes_save: defaultdict[tuple[str, ...], list[NodeModel]] = field(default_factory=lambda: defaultdict(list))
    _pending_nodes_delete: list[str] = field(default_factory=list)

    _pending_edges_save: defaultdict[str, list[EdgeModel]] = field(default_factory=lambda: defaultdict(list))
    _pending_edges_delete: defaultdict[str, list[EdgeModel]] = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self):
        self._session = self.driver.session()
        self._transaction = self._session.begin_transaction()

    # ==========================================
    # 辅助反射方法
    # ==========================================

    @classmethod
    def _get_edge_fields(cls, model_class: type[BaseModel]) -> dict[str, RelationshipMeta]:
        """从 Pydantic 模型的 Annotated 中提取图谱关系元数据"""
        edge_fields = {}
        for field_name, field_info in model_class.model_fields.items():
            for meta_item in field_info.metadata:
                if isinstance(meta_item, RelationshipMeta):
                    edge_fields[field_name] = meta_item
        return edge_fields

    # ==========================================
    # 生命周期管理 (UoW)
    # ==========================================

    def flush(self) -> None:
        """将内存中的所有挂起状态转化为 Cypher 语句执行"""
        self._flush_nodes_save()
        self._flush_edges_save()
        self._flush_edges_delete()
        self._flush_nodes_delete()

    def commit(self) -> None:
        try:
            self.flush()
            self._transaction.commit()
        finally:
            self.close()

    def rollback(self) -> None:
        try:
            self._transaction.rollback()
        finally:
            self.close()

    def close(self) -> None:
        if hasattr(self, "_session") and self._session:
            self._session.close()

    # ==========================================
    # 状态收集 (Write / Command)
    # ==========================================

    def save_node(self, model: NodeModel) -> None:
        # 直接存储模型实例，推迟字典化和清洗操作至 flush 阶段
        self._pending_nodes_save[model.__labels__].append(model)

    def delete_node(self, node_id: str) -> None:
        self._pending_nodes_delete.append(node_id)

    def save_edge(self, edge_model: EdgeModel) -> None:
        self._pending_edges_save[edge_model.__rel_type__].append(edge_model)

    def delete_edge(self, edge_model: EdgeModel) -> None:
        self._pending_edges_delete[edge_model.__rel_type__].append(edge_model)

    # ==========================================
    # 数据查询 (Read / Query)
    # ==========================================

    def execute(self, query: str, **parameters: Any) -> Result:
        self.flush()
        return self._transaction.run(query, **parameters)

    def get(self, model_class: type[TNode], node_id: str) -> TNode | None:
        """统一的单节点查询入口，自动解析 Annotated 元数据并装配关系"""
        self.flush()

        labels_str = ":" + ":".join(getattr(model_class, "__labels__", ()))
        edge_fields = self._get_edge_fields(model_class)

        match_clauses = [f"MATCH (n{labels_str} {{id: $id}})"]
        return_clauses = ["n"]

        # 根据 RelationshipMeta 动态拼接 OPTIONAL MATCH
        for field_name, meta in edge_fields.items():
            rel_type = meta.edge_model.__rel_type__
            
            # 处理箭头方向
            left_arrow = "<-" if meta.direction == RelationDirection.IN else "-"
            right_arrow = "->" if meta.direction == RelationDirection.OUT else "-"

            target_alias = f"{field_name}_target"

            match_clauses.append(
                f"OPTIONAL MATCH (n){left_arrow}[:{rel_type}]{right_arrow}({target_alias})"
            )
            # 聚合目标属性 (这里默认取 meta.target_property，通常为 "id")
            return_clauses.append(
                f"collect(DISTINCT {target_alias}.{meta.target_property}) AS {field_name}"
            )

        query = "\n".join(match_clauses) + "\nRETURN " + ",\n".join(return_clauses)
        
        result = self._transaction.run(query, id=node_id).single()
        if not result:
            return None

        # 将主节点属性与聚合后的关联属性合并
        node_props = dict(result["n"])
        for field_name in edge_fields.keys():
            node_props[field_name] = result[field_name]

        # 直接交给 Pydantic 反序列化
        return model_class(**node_props)

    # ==========================================
    # 内部私有执行逻辑 (Batch Execution)
    # ==========================================

    def _flush_nodes_save(self) -> None:
        for labels, models in self._pending_nodes_save.items():
            if not models:
                continue
            
            label_str = ":" + ":".join(labels)
            model_class = models[0].__class__
            
            # 获取需要被排除的关系字段（不在节点自身持久化）
            edge_field_names = set(self._get_edge_fields(model_class).keys())
            
            batch = []
            for m in models:
                # 使用 Pydantic 的 exclude 参数剔除边数据
                props = m.model_dump(exclude=edge_field_names)
                batch.append({"id": m.id, "props": props})

            query = f"""
            UNWIND $batch AS item
            MERGE (n{label_str} {{id: item.id}})
            SET n += item.props
            """
            self._transaction.run(query, batch=batch)
            
        self._pending_nodes_save.clear()

    def _flush_edges_save(self) -> None:
        for rel_type, edges in self._pending_edges_save.items():
            if not edges:
                continue
                
            batch = []
            for e in edges:
                # 剔除 source_id 和 target_id，剩下的作为边属性持久化
                props = e.model_dump(exclude={"source_id", "target_id"})
                batch.append({
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "props": props
                })

            query = f"""
            UNWIND $batch AS edge
            MATCH (s {{id: edge.source_id}}), (t {{id: edge.target_id}})
            MERGE (s)-[r:{rel_type}]->(t)
            SET r += edge.props
            """
            self._transaction.run(query, batch=batch)
            
        self._pending_edges_save.clear()

    def _flush_edges_delete(self) -> None:
        for rel_type, edges in self._pending_edges_delete.items():
            if not edges:
                continue
                
            batch = [{"source_id": e.source_id, "target_id": e.target_id} for e in edges]
            
            query = f"""
            UNWIND $batch AS edge
            MATCH (s {{id: edge.source_id}})-[r:{rel_type}]->(t {{id: edge.target_id}})
            DELETE r
            """
            self._transaction.run(query, batch=batch)
            
        self._pending_edges_delete.clear()

    def _flush_nodes_delete(self) -> None:
        if not self._pending_nodes_delete:
            return
            
        query = """
        UNWIND $batch AS id
        MATCH (n {id: id})
        DETACH DELETE n
        """
        self._transaction.run(query, batch=self._pending_nodes_delete)
        self._pending_nodes_delete.clear()