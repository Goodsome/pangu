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

    _pending_nodes_save: defaultdict[tuple[str, ...], list[NodeModel]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _pending_nodes_delete: list[str] = field(default_factory=list)

    _pending_edges_save: defaultdict[type[EdgeModel], list[EdgeModel]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _pending_edges_delete: defaultdict[type[EdgeModel], list[EdgeModel]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def __post_init__(self):
        self._session = self.driver.session()
        self._transaction = self._session.begin_transaction()

    # ==========================================
    # 辅助反射方法
    # ==========================================

    @classmethod
    def _get_edge_fields(
        cls, model_class: type[BaseModel]
    ) -> dict[str, RelationshipMeta]:
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
        self._pending_edges_save[type(edge_model)].append(edge_model)

    def delete_edge(self, edge_model: EdgeModel) -> None:
        self._pending_edges_delete[type(edge_model)].append(edge_model)

    # ==========================================
    # 数据查询 (Read / Query)
    # ==========================================

    def execute(self, query: str, **parameters: Any) -> Result:
        self.flush()
        return self._transaction.run(query, **parameters)

    def get(self, model_class: type[TNode], node_id: str) -> TNode | None:
        """统一的单节点查询入口，自动解析 Annotated 元数据并装配关系"""
        nodes = self.find(model_class, id=node_id)
        if not nodes:
            return None
        return nodes[0]

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
        for edge_cls, edges in self._pending_edges_save.items():
            if not edges:
                continue

            batch: list[dict[str, object]] = []
            rel_type = edge_cls.__rel_type__
            s_key = edge_cls.__source_key__
            t_key = edge_cls.__target_key__
            s_label = edge_cls.__source_model__.get_label_string()
            t_label = edge_cls.__target_model__.get_label_string()

            for e in edges:
                props = e.model_dump(exclude={"source_ref", "target_ref"})
                batch.append(
                    {
                        "source_ref": e.source_ref,
                        "target_ref": e.target_ref,
                        "props": props,
                    }
                )

            query = f"""
            UNWIND $batch AS edge
            MATCH (s{s_label} {{{s_key}: edge.source_ref}})
            MATCH (t{t_label} {{{t_key}: edge.target_ref}})
            MERGE (s)-[r:{rel_type}]->(t)
            SET r += edge.props
            """
            self._transaction.run(query, batch=batch)

        self._pending_edges_save.clear()

    def _flush_edges_delete(self) -> None:
        for edge_cls, edges in self._pending_edges_delete.items():
            if not edges:
                continue

            batch = [
                {"source_ref": e.source_ref, "target_ref": e.target_ref} for e in edges
            ]
            rel_type = edge_cls.__rel_type__
            s_key = edge_cls.__source_key__
            t_key = edge_cls.__target_key__
            s_label = edge_cls.__source_model__.get_label_string()
            t_label = edge_cls.__target_model__.get_label_string()

            query = f"""
            UNWIND $batch AS edge
            MATCH (s{s_label} {{{s_key}: edge.source_ref}})-[r:{rel_type}]->(t{t_label} {{{t_key}: edge.target_ref}})
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

    def _build_projection_clauses(
        self, model_class: type[NodeModel], root_alias: str = "n"
    ) -> tuple[list[str], list[str], list[str]]:
        """
        内部方法：提取模型上的关系声明，生成对应的关系查询和聚合子句。
        返回: (可选匹配子句列表, 返回子句列表, 边属性键名列表)
        """
        edge_fields = self._get_edge_fields(model_class)
        match_clauses = []
        return_clauses = [root_alias]
        edge_keys = list(edge_fields.keys())
        source_match = root_alias + model_class.get_label_string()

        for field_name, meta in edge_fields.items():
            edge_cls = EdgeModel.get_cls(meta.edge_model)
            rel_type = edge_cls.__rel_type__
            left_arrow = "<-" if meta.direction == RelationDirection.IN else "-"
            right_arrow = "->" if meta.direction == RelationDirection.OUT else "-"

            target_alias = f"{field_name}_target"
            target_match = target_alias

            match meta.target_model:
                case None:
                    target_cls = edge_cls.__target_model__
                case str():
                    target_cls = NodeModel.get_cls(meta.target_model)
                case _:
                    target_cls = meta.target_model

            target_match += target_cls.get_label_string()

            match_clauses.append(
                f"OPTIONAL MATCH ({source_match}){left_arrow}[:{rel_type}]{right_arrow}({target_match})"
            )
            return_clauses.append(
                f"collect(DISTINCT {target_alias}.{meta.target_property}) AS {field_name}"
            )

        return match_clauses, return_clauses, edge_keys

    def find(self, model_class: type[TNode], **kwargs: Any) -> list[TNode]:
        """通用的节点查询方法，支持多条件匹配及列表查询"""
        self.flush()

        labels_str = ":" + ":".join(getattr(model_class, "__labels__", ()))
        query_parts = [f"MATCH (n{labels_str})"]

        # 动态构建 WHERE 条件
        where_clauses = []
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple, set)):
                where_clauses.append(f"n.{key} IN ${key}")
            else:
                where_clauses.append(f"n.{key} = ${key}")

        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))

        # 追加关系投射子句
        opt_matches, returns, edge_keys = self._build_projection_clauses(
            model_class, root_alias="n"
        )
        query_parts.extend(opt_matches)
        query_parts.append("RETURN " + ",\n".join(returns))

        query = "\n".join(query_parts)

        # 执行查询并组装结果
        result = self._transaction.run(query, **kwargs)

        nodes = []
        for record in result:
            node_props = dict(record["n"])
            # 合并聚合的边属性
            for edge_key in edge_keys:
                node_props[edge_key] = record[edge_key]
            nodes.append(model_class(**node_props))

        return nodes
