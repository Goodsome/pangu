from dataclasses import dataclass
from pathlib import Path
from typing import assert_never

from architecture.domain.aggregates.module import Module
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.services.context_registry import ContextRegistry
from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.domain.value_objects.parsed_edge import ParsedEdge
from architecture.domain.value_objects.parsed_module import ParsedModule
from architecture.enums.context_name import ContextName
from architecture.enums.edge_kind import EdgeKind


@dataclass
class GraphBuilder:
    module_registry: dict[ModuleFqn, Module]

    def build_from_parsed_modules(self, parsed_modules: list[ParsedModule]):

        parsed_edges: list[ParsedEdge] = []
        for parsed_module in parsed_modules:
            fqn = self._path_to_fqn(parsed_module.file_path)
            is_package = parsed_module.file_path.name == "__init__.py"
            module = Module(
                id=ModuleId.create(),
                fqn=fqn,
                name=fqn.symbol,
                is_package=is_package,
            )
            self.module_registry[module.fqn] = module

            if not fqn.is_root:
                parsed_edges.append(
                    ParsedEdge(
                        kind=EdgeKind.CONTAINS,
                        source=fqn.parent_fqn,
                        target=fqn,
                    )
                )

            for import_str in parsed_module.raw_imports:
                target_fqn = self._module_path_to_fqn(import_str)
                if target_fqn.context not in ContextName._value2member_map_:
                    continue
                parsed_edges.append(
                    ParsedEdge(
                        kind=EdgeKind.DEPENDS_ON,
                        source=fqn,
                        target=target_fqn,
                    )
                )
        for parsed_edge in parsed_edges:
            self._build_edge(parsed_edge)

    def _path_to_fqn(self, path: Path) -> ModuleFqn:
        rel_path = ContextRegistry.get_relative_path(path)
        if rel_path.name == "__init__.py":
            return ModuleFqn(".".join(rel_path.parent.parts))
        return ModuleFqn(".".join(rel_path.with_suffix("").parts))

    def _module_path_to_fqn(self, path: str) -> ModuleFqn:
        return ModuleFqn(path)

    def _build_contains_edge(
        self, parent_fqn: ModuleFqn, target_fqn: ModuleFqn
    ) -> None:
        if target_fqn.is_root:
            return
        if parent_fqn not in self.module_registry:
            parent = Module.create(
                fqn=parent_fqn,
                name=parent_fqn.symbol,
                is_package=True,
            )
            self.module_registry[parent_fqn] = parent
        parent = self.module_registry[parent_fqn]
        module = self.module_registry[target_fqn]
        parent.add_contains(module.id)

    def _build_edge(self, parsed_edge: ParsedEdge) -> None:
        match parsed_edge.kind:
            case EdgeKind.DEPENDS_ON:
                source = self.module_registry[parsed_edge.source]
                target = self.module_registry[parsed_edge.target]
                source.add_dependency(target.id)
            case EdgeKind.CONTAINS:
                self._build_contains_edge(parsed_edge.source, parsed_edge.target)
            case _:
                assert_never(parsed_edge.kind)
