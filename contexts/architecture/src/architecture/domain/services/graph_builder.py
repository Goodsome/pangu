from dataclasses import dataclass
from pathlib import Path
from typing import assert_never
from architecture.domain.aggregates.module import Module
from foundation.common_types.identities.module_id import ModuleId
from architecture.domain.services.context_registry import ContextRegistry
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.domain.value_objects.parsed_edge import ParsedEdge
from architecture.domain.value_objects.parsed_module import ParsedModule
from foundation.common_types.context_name import ContextName
from architecture.domain.enums.edge_kind import EdgeKind


@dataclass
class GraphBuilder:
    module_registry: dict[ModuleFqn, Module]

    def build_from_parsed_modules(self, parsed_modules: list[ParsedModule]):
        contains_edges: list[ParsedEdge] = []
        depends_on_edges: list[ParsedEdge] = []
        for parsed_module in parsed_modules:
            fqn = parsed_module.fqn
            is_package = parsed_module.is_package
            module = Module(
                id=ModuleId.create(), fqn=fqn, name=fqn.symbol, is_package=is_package
            )
            self.module_registry[module.fqn] = module
            if not fqn.is_root:
                contains_edges.append(
                    ParsedEdge(
                        kind=EdgeKind.CONTAINS, source=fqn.parent_fqn, target=fqn
                    )
                )
            for import_str in parsed_module.import_module_fqns:
                target_fqn = import_str
                if target_fqn.context not in ContextName._value2member_map_:
                    continue
                depends_on_edges.append(
                    ParsedEdge(kind=EdgeKind.DEPENDS_ON, source=fqn, target=target_fqn)
                )
        for parsed_edge in contains_edges:
            self._build_contains_edge(parsed_edge)
        for parsed_edge in depends_on_edges:
            self._build_depends_on_edge(parsed_edge)

    def _path_to_fqn(self, path: Path) -> ModuleFqn:
        rel_path = ContextRegistry.get_relative_path(path)
        if rel_path.name == "__init__.py":
            return ModuleFqn(".".join(rel_path.parent.parts))
        return ModuleFqn(".".join(rel_path.with_suffix("").parts))

    def _module_path_to_fqn(self, path: str) -> ModuleFqn:
        return ModuleFqn(path)

    def _build_contains_edge(self, parsed_edge: ParsedEdge) -> None:
        if parsed_edge.kind != EdgeKind.CONTAINS:
            return
        target_fqn = parsed_edge.target
        parent_fqn = parsed_edge.source
        if target_fqn.is_root:
            return
        if parent_fqn not in self.module_registry:
            parent = Module.create(
                fqn=parent_fqn, name=parent_fqn.symbol, is_package=True
            )
            self.module_registry[parent_fqn] = parent
        parent = self.module_registry[parent_fqn]
        module = self.module_registry[target_fqn]
        parent.add_contains(module.id)

    def _build_depends_on_edge(self, parsed_edge: ParsedEdge) -> None:
        if parsed_edge.kind != EdgeKind.DEPENDS_ON:
            return
        source = self.module_registry[parsed_edge.source]
        target = self.module_registry[parsed_edge.target]
        source.add_dependency(target.id)

    def _build_edge(self, parsed_edge: ParsedEdge) -> None:
        match parsed_edge.kind:
            case EdgeKind.DEPENDS_ON:
                self._build_depends_on_edge(parsed_edge)
            case EdgeKind.CONTAINS:
                self._build_contains_edge(parsed_edge)
            case _:
                assert_never(parsed_edge.kind)
