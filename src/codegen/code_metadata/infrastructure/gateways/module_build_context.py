from dataclasses import dataclass
from dataclasses import field
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import ExternalNode
from codegen.code_metadata.domain.aggregates.code_node import FunctionNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge
from codegen.code_metadata.infrastructure.gateways.class_edge_builder import (
    ClassEdgeBuilder,
)


@dataclass
class ModuleBuildContext:
    module: ModuleNode
    code_document: CodeDocument
    node_registry: NodeRegistry
    local_aliases: dict[str, str] = field(init=False)

    def __post_init__(self):
        self.local_aliases = {}
        for edge in self.module.outbound_edges:
            if edge.kind is not EdgeType.DEFINES:
                continue
            target_name = edge.fqn.split("::")[-1]
            self.local_aliases[target_name] = edge.fqn

    def build(self):
        for stmt in self.code_document.body:
            self._parse_stmt(stmt)
        return self.module

    def _parse_stmt(self, stmt: AstStmt):
        match stmt:
            case (
                AstImport() | AstImportFrom() | AstIf(test=AstName(id="TYPE_CHECKING"))
            ):
                self._build_import_edges(stmt)
            case AstClassDef():
                self._build_class_edge(stmt)
            case _:
                pass

    def _build_import_edges(
        self, stmt: AstStmt, is_type_checking: bool = False
    ) -> None:
        match stmt:
            case AstImport():
                self._parse_import(stmt, is_type_checking)
            case AstImportFrom():
                self._parse_import_from(stmt, is_type_checking)
            case AstIf(test=AstName(id="TYPE_CHECKING")):
                for subnode in stmt.body:
                    self._build_import_edges(subnode, is_type_checking=True)
            case _:
                raise ValueError(f"Unexpected statement type: stmt={stmt!r}")

    def _parse_import(self, import_: AstImport, is_type_checking: bool = False) -> None:
        for name in import_.names:
            self._parse_import_name(
                name.name, asname=name.asname, is_type_checking=is_type_checking
            )

    def _parse_import_from(
        self, import_from: AstImportFrom, is_type_checking: bool = False
    ) -> None:
        if import_from.level > 0:
            relative_level = import_from.level
            if self.module.is_package:
                relative_level = relative_level - 1
            module_prefix = self.module.get_parent_by_level(relative_level)
        else:
            module_prefix = ""
        module = import_from.module or ""
        if module_prefix:
            module = module_prefix + "." + module
        if not module:
            raise ValueError(f"ImportFrom module is empty: {import_from.module}")
        for name in import_from.names:
            self._parse_import_name(
                name.name,
                from_name=module,
                asname=name.asname,
                is_type_checking=is_type_checking,
            )

    def _parse_import_name(
        self,
        import_name: str,
        from_name: str | None = None,
        asname: str | None = None,
        is_type_checking: bool = False,
    ) -> None:
        if from_name:
            is_external = not from_name.startswith("codegen.")
        else:
            is_external = not import_name.startswith("codegen.")
        if is_external:
            external_fqn = f"{from_name}.{import_name}" if from_name else import_name
            node = self.node_registry.get_node(external_fqn)
        else:
            node = self._get_internel_node(import_name=import_name, from_name=from_name)
        assert isinstance(node, ExternalNode | ClassNode | FunctionNode | VariableNode)
        self.module.imports(node, is_type_checking=is_type_checking, asname=asname)
        if asname:
            local_alias_key = asname
        else:
            local_alias_key = node.name
        self.local_aliases[local_alias_key] = node.fqn

    def _add_node(self, dto: CodeNode) -> None:
        self.node_registry.add_node(dto)

    def _get_internel_node(self, import_name: str, from_name: str | None) -> CodeNode:
        name = import_name
        if from_name is None:
            return self.node_registry.get_node(name)
        from_module = self.node_registry.get_node(from_name)
        for edge in from_module.outbound_edges:
            if edge.node_name == import_name:
                node = self.node_registry.get_node(edge.fqn)
                return node
        raise ValueError(f"{import_name} not found in {from_name}")

    def _build_class_edge(self, class_def: AstClassDef):
        class_fqn = f"{self.module.fqn}::{class_def.name}"
        node = self.node_registry.get_node(class_fqn)
        assert isinstance(node, ClassNode)
        class_edge_builder = ClassEdgeBuilder(
            class_node=node,
            class_def=class_def,
            node_registry=self.node_registry,
            local_aliases=self.local_aliases,
        )
        class_edge_builder.build()
