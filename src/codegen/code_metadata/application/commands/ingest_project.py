from pathlib import Path
import uuid
from dataclasses import dataclass
from codegen.code_metadata.application.dtos.ingest_project_command import (
    IngestProjectCommand,
)
from codegen.code_metadata.application.dtos.ingest_project_result import (
    IngestProjectResult,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)
from codegen.code_metadata.application.registry.node_registry import NodeRegistry


@dataclass
class IngestProject:
    """将一个 bounded context 下的目录结构扫描入库为 CodeNode 图。"""

    graph_builder: CodeGraphBuilder
    sync_service: CodeNodeSyncService
    query_service: CodeNodeQueryService

    def execute(self, cmd: IngestProjectCommand) -> IngestProjectResult:
        sync_id = uuid.uuid4().hex
        fqn_prefix = "codegen."
        if cmd.prefix:
            fqn_prefix = f"codegen.{cmd.prefix}"
        module_path = Path("src") / fqn_prefix.replace(".", "/")
        code_documents = self.graph_builder.get_code_documents(module_path=module_path)
        node_reistry: NodeRegistry = NodeRegistry()
        imports = self.graph_builder.build_nodes(
            root_path=module_path,
            node_registry=node_reistry,
            code_documents=code_documents,
        )
        query_imports: set[str] = set()
        for import_module_fqn in imports:
            if node_reistry.find_node(import_module_fqn):
                continue
            query_imports.add(import_module_fqn)
        query_nodes = self.query_service.find_by_fqns(
            query_imports, with_outbounds=True
        )
        node_reistry.registry_nodes(query_nodes)
        self.graph_builder.build_edges(
            node_registry=node_reistry, code_documents=code_documents
        )
        bulk_result = self.sync_service.save_nodes_bulk(
            node_reistry.upsert_nodes, sync_id, fqn_prefix
        )
        deleted_count = self.sync_service.delete_stale_nodes(fqn_prefix, sync_id)
        return IngestProjectResult(
            nodes_created=bulk_result.nodes_upserted,
            edges_created=bulk_result.edges_created,
            nodes_deleted=deleted_count,
        )
