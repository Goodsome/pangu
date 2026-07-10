from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, TypeVar, cast, LiteralString

from neo4j import Driver, Result, Session, Transaction

from foundation.persistence.orm.neo4j_base import (
    EdgeModel,
    NodeModel,
    RelationDirection,
    RelationshipMeta,
    Rel,
    EdgeItem,
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

    _snapshots: dict[str, NodeModel] = field(default_factory=dict)

    def __post_init__(self):
        self._session = self.driver.session()
        self._transaction = self._session.begin_transaction()

    # ==========================================
    # 辅助反射方法
    # ==========================================

    @classmethod
    def _get_edge_fields(
        cls, model_class: type[NodeModel]
    ) -> dict[str, dict[str, Any]]:
        """从 Pydantic 模型提取图谱关系元数据，支持新型泛型 Rel 声明和旧的 RelationshipMeta"""
        edge_fields = {}
        for field_name, field_info in model_class.model_fields.items():
            # 1. 解析新型泛型声明
            annotation = field_info.annotation
            if isinstance(annotation, type) and issubclass(annotation, Rel):
                edge_cls = annotation.get_edge_cls()
                if isinstance(edge_cls, str):
                    edge_cls = EdgeModel.get_cls(edge_cls)
                    
                target_cls = annotation.get_target_cls()
                if isinstance(target_cls, str):
                    target_cls = NodeModel.get_cls(target_cls)
                    
                edge_fields[field_name] = {
                    "edge_cls": edge_cls,
                    "target_cls": target_cls,
                    "direction": annotation.get_direction(),
                    "projection": annotation.get_projection_type(),
                    "is_legacy": False
                }
                continue

            metadata = []
            if (
                isinstance(field_info.json_schema_extra, dict)
                and "metadata" in field_info.json_schema_extra
            ):
                val = field_info.json_schema_extra["metadata"]
                if isinstance(val, list):
                    metadata = val
            elif isinstance(field_info.metadata, list):
                metadata = field_info.metadata

            for meta_item in metadata:
                if isinstance(meta_item, RelationshipMeta):
                    edge_cls = EdgeModel.get_cls(meta_item.edge_model)
                    if isinstance(meta_item.target_model, str):
                        target_cls = NodeModel.get_cls(meta_item.target_model)
                    elif meta_item.target_model is not None:
                        target_cls = meta_item.target_model
                    else:
                        target_cls = edge_cls.__target_model__

                    proj = "meta_id" if meta_item.target_property else "meta_node"

                    edge_fields[field_name] = {
                        "edge_cls": edge_cls,
                        "target_cls": target_cls,
                        "direction": meta_item.direction,
                        "projection": proj,
                        "is_legacy": True,
                        "meta": meta_item,
                    }
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

    def save_node(self, node: NodeModel) -> None:
        """
        基于 Snapshot 的智能写入入口。
        比对当前 node 与查询时的快照，自动拆解为增量的点/边 CREATE/UPDATE/DELETE，并存入待处理队列。
        """
        old_node = self._snapshots.get(node.id)
        edge_fields = self._get_edge_fields(type(node))
        edge_field_names = set(edge_fields.keys())
        
        # 1. 存储/更新 Node 自身标量属性
        if not old_node:
            self._pending_nodes_save[node.__labels__].append(node)
        else:
            old_props = old_node.model_dump(exclude=edge_field_names)
            new_props = node.model_dump(exclude=edge_field_names)
            if old_props != new_props:
                self._pending_nodes_save[node.__labels__].append(node)
                
        # 2. 对比关系集合
        def extract_edge_info(items: Any, info: dict[str, Any], current_node_id: str) -> dict[str, EdgeModel]:
            proj = info["projection"]
            edge_cls = info["edge_cls"]
            direction = info["direction"]
            result = {}
            for item in items:
                if proj == "edge":
                    other_id = item.source_ref if direction == RelationDirection.IN else item.target_ref
                    result[other_id] = item
                elif proj == "relation":
                    other_id = item.target.id if hasattr(item.target, "id") else item.target
                    result[other_id] = item.edge
                else: # node / meta_node / meta_id
                    other_id = item.id if hasattr(item, "id") else item
                    s_ref = other_id if direction == RelationDirection.IN else current_node_id
                    t_ref = current_node_id if direction == RelationDirection.IN else other_id
                    result[other_id] = edge_cls(source_ref=s_ref, target_ref=t_ref)
            return result
            
        for field_name, info in edge_fields.items():
            old_rel = getattr(old_node, field_name) if old_node else None
            new_rel = getattr(node, field_name)
            
            old_items = getattr(old_rel, "items", old_rel) if old_rel is not None else []
            new_items = getattr(new_rel, "items", new_rel) if new_rel is not None else []
            
            old_map = extract_edge_info(old_items, info, node.id)
            new_map = extract_edge_info(new_items, info, node.id)
            
            added = set(new_map.keys()) - set(old_map.keys())
            removed = set(old_map.keys()) - set(new_map.keys())
            kept = set(old_map.keys()) & set(new_map.keys())
            
            for t_id in added:
                self.save_edge(new_map[t_id])
                
            for t_id in removed:
                self.delete_edge(old_map[t_id])
                
            for t_id in kept:
                old_edge = old_map[t_id]
                new_edge = new_map[t_id]
                if old_edge and new_edge:
                    if old_edge.model_dump(exclude={"source_ref", "target_ref"}) != new_edge.model_dump(exclude={"source_ref", "target_ref"}):
                        self.save_edge(new_edge)
                        
        # 3. 将新的 node 设置为未来可能的 snapshot
        self._snapshots[node.id] = node.model_copy(deep=True)

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
        return self._transaction.run(cast(LiteralString, query), **parameters)

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
            self._transaction.run(cast(LiteralString, query), batch=batch)

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
            self._transaction.run(cast(LiteralString, query), batch=batch)

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
            self._transaction.run(cast(LiteralString, query), batch=batch)

        self._pending_edges_delete.clear()

    def _flush_nodes_delete(self) -> None:
        if not self._pending_nodes_delete:
            return

        query = """
        UNWIND $batch AS id
        MATCH (n {id: id})
        DETACH DELETE n
        """
        self._transaction.run(
            cast(LiteralString, query), batch=self._pending_nodes_delete
        )
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

        for field_name, info in edge_fields.items():
            edge_cls = info["edge_cls"]
            target_cls = info["target_cls"]
            direction = info["direction"]
            proj = info["projection"]

            rel_type = edge_cls.__rel_type__
            left_arrow = "<-" if direction == RelationDirection.IN else "-"
            right_arrow = "->" if direction == RelationDirection.OUT else "-"

            target_alias = f"{field_name}_target"
            rel_alias = f"{field_name}_rel"
            target_match = target_alias + target_cls.get_label_string()

            match_clauses.append(
                f"OPTIONAL MATCH ({source_match}){left_arrow}[{rel_alias}:{rel_type}]{right_arrow}({target_match})"
            )

            if proj == "edge":
                return_clauses.append(
                    f"collect(DISTINCT CASE WHEN {rel_alias} IS NOT NULL THEN {rel_alias} {{.*, source_ref: {root_alias}.id, target_ref: {target_alias}.id}} END) AS {field_name}"
                )
            elif proj == "node" or proj == "meta_node":
                return_clauses.append(
                    f"collect(DISTINCT CASE WHEN {target_alias} IS NOT NULL THEN properties({target_alias}) END) AS {field_name}"
                )
            elif proj == "relation":
                return_clauses.append(
                    f"collect(DISTINCT CASE WHEN {target_alias} IS NOT NULL THEN {{edge: {rel_alias} {{.*, source_ref: {root_alias}.id, target_ref: {target_alias}.id}}, target: properties({target_alias})}} END) AS {field_name}"
                )
            elif proj == "meta_id":
                target_prop = info["meta"].target_property
                return_clauses.append(
                    f"collect(DISTINCT {target_alias}.{target_prop}) AS {field_name}"
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
        result = self._transaction.run(cast(LiteralString, query), **kwargs)

        edge_fields = self._get_edge_fields(model_class)

        nodes = []
        for record in result:
            node_props = dict(record["n"])
            # 合并聚合的边属性
            for edge_key in edge_keys:
                raw = record[edge_key]
                info = edge_fields[edge_key]
                proj = info["projection"]
                edge_cls = info["edge_cls"]
                target_cls = info["target_cls"]

                if proj == "edge":
                    items = [edge_cls(**item) for item in raw]
                    node_props[edge_key] = {"items": items}
                elif proj == "node":
                    items = [target_cls(**item) for item in raw]
                    node_props[edge_key] = {"items": items}
                elif proj == "relation":
                    items = [
                        EdgeItem(
                            edge=edge_cls(**item["edge"]),
                            target=target_cls(**item["target"]),
                        )
                        for item in raw
                    ]
                    node_props[edge_key] = {"items": items}
                elif proj == "meta_node":
                    node_props[edge_key] = [target_cls(**item) for item in raw]
                else:
                    node_props[edge_key] = raw

            node = model_class(**node_props)
            nodes.append(node)
            self._snapshots[node.id] = node.model_copy(deep=True)

        return nodes
