from dataclasses import dataclass
from pydantic import BaseModel
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.application.ports.file_differ import FileDiffer
from codegen.code_metadata.application.registry.node_registry import NodeRegistry


class GetDevProgressQuery(BaseModel):
    module_fqn: str


@dataclass
class GetDevProgressHandler:
    query_service: CodeNodeQueryService
    file_differ: FileDiffer

    def execute(self, query: GetDevProgressQuery) -> DevProgress:
        nodes = self.query_service.find_by_fqn_prefix(query.module_fqn)
        registry = NodeRegistry.create(nodes=nodes)
        dev_progress = DevProgress()
        for node in nodes:
            if not isinstance(node, ModuleNode):
                continue
            file_metrics = self.file_differ.get_diff_metric(node, registry)
            dev_progress.add_record(file_metrics)
        return dev_progress
