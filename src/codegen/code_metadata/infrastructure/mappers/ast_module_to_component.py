import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_module import ParsedDirectoryModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_attribute import (
    AstNodeToAttribute,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import (
    AstNodeToParsedType,
)
from codegen.code_metadata.infrastructure.mappers.ast_to_behavior_mixin import (
    AstToBehaviorMixin,
)

logger = logging.getLogger(__name__)


@dataclass
class AstModuleToComponent(
    AstToBehaviorMixin, AstClassToComponent, AstNodeToParsedType, AstNodeToAttribute
):
    _CODEGEN_PREFIX: ClassVar[str] = "codegen."

    def parse_node_to_behavior(self, node: ast.AST) -> ParsedBehavior:
        match node:
            case ast.FunctionDef():
                return self.function_def_to_behavior(node)
            case _:
                raise ValueError(f"not support node={node!r}")

    def parse_node_to_attribute(self, node: ast.AST) -> ParsedAttribute:
        match node:
            case ast.AnnAssign():
                return self.ann_assign_to_attribute(node)
            case ast.Assign():
                return self.assign_to_attribute(node)
            case ast.arg():
                return self.arg_to_attribute(node)
            case _:
                raise ValueError(f"not support node={node!r}")

    def parse_node_to_attributes(self, node: ast.arguments) -> list[ParsedAttribute]:
        return self._parse_node_to_attributes(node)

    def parse_node_to_type(self, node: ast.AST) -> ParsedType:
        return self._node_to_type(node)

    def map(self, module: ast.Module, component_name: str) -> ParsedComponent:
        component: ParsedComponent | None = None
        imports: list[ImportDto] = []
        for node in module.body:
            imports.extend(self.try_get_imports(node))
        for node in module.body:
            component = self.try_get_component(node, component_name, imports=imports)
            if component:
                break
        if component is None:
            raise ValueError(f"No class definition found in module {component_name}")
        component.imports = imports
        return component

    def try_get_component(
        self, node: ast.AST, component_name: str, imports: list[ImportDto]
    ) -> ParsedComponent | None:
        if isinstance(node, ast.ClassDef) and node.name == component_name:
            return self.class_def_to_component(node, imports=imports)
        elif isinstance(node, ast.Assign):
            return self.parse_assign(node)
        return None

    def try_get_imports(
        self, node: ast.stmt, type_checking: bool = False
    ) -> list[ImportDto]:
        if isinstance(node, ast.ImportFrom):
            return [
                ImportDto(
                    module=node.module,
                    names=[a.name for a in node.names],
                    level=node.level,
                    type_checking=type_checking,
                )
            ]
        elif isinstance(node, ast.Import):
            return [
                ImportDto(module=a.name, names=[], level=0, type_checking=type_checking)
                for a in node.names
            ]
        elif isinstance(node, ast.If):
            imports: list[ImportDto] = []
            for subnode in node.body:
                imports.extend(self.try_get_imports(subnode, type_checking=True))
            for subnode in node.orelse:
                imports.extend(self.try_get_imports(subnode, type_checking=True))
            return imports
        return []

    def parse_assign(self, node: ast.Assign) -> ParsedComponent | None:
        if len(node.targets) != 1:
            return None
        if not isinstance(node.targets[0], ast.Name):
            return None
        name = node.targets[0].id
        if not isinstance(node.value, ast.Subscript):
            return None
        is_annotated = False
        if (
            isinstance(node.value.value, ast.Name)
            and node.value.value.id == "Annotated"
        ):
            is_annotated = True
        elif (
            isinstance(node.value.value, ast.Attribute)
            and isinstance(node.value.value.value, ast.Name)
            and (node.value.value.value.id in ("typing", "typing_extensions"))
            and (node.value.value.attr == "Annotated")
        ):
            is_annotated = True
        if not is_annotated:
            return None
        if not isinstance(node.value.slice, ast.Tuple):
            return None
        elts = node.value.slice.elts
        if len(elts) < 2:
            return None
        members = self._extract_union_members(elts[0])
        if not members:
            return None
        discriminator = None
        for metadata_node in elts[1:]:
            if (
                isinstance(metadata_node, ast.Call)
                and isinstance(metadata_node.func, ast.Name)
                and (metadata_node.func.id == "Field")
            ):
                for kw in metadata_node.keywords:
                    if (
                        kw.arg == "discriminator"
                        and isinstance(kw.value, ast.Constant)
                        and isinstance(kw.value.value, str)
                    ):
                        discriminator = kw.value.value
                        break
                if discriminator:
                    break
        if not discriminator:
            return None
        return ParsedComponent(
            name=name,
            description="",
            attributes=[],
            behaviors=[],
            bases=[],
            imports=[],
            members=members,
            discriminator=discriminator,
        )

    def _extract_union_members(self, type_node: ast.AST) -> list[str] | None:
        if isinstance(type_node, ast.Name):
            return [type_node.id]
        elif isinstance(type_node, ast.BinOp) and isinstance(type_node.op, ast.BitOr):
            left_m = self._extract_union_members(type_node.left)
            right_m = self._extract_union_members(type_node.right)
            if left_m is not None and right_m is not None:
                return left_m + right_m
        return None

    def parse_module(self, module: ast.Module, path: Path) -> ParsedFileModule:
        imports: list[ImportDto] = []
        components: list[ParsedComponent] = []
        for node in module.body:
            match node:
                case (
                    ast.ImportFrom()
                    | ast.Import()
                    | ast.If(test=ast.Name(id="TYPE_CHECKING"))
                ):
                    imports.extend(self.try_get_imports(node))
                case ast.ClassDef():
                    components.append(self.class_def_to_component(node, imports=[]))
                case ast.Assign():
                    c = self.parse_assign(node)
                    if c is not None:
                        components.append(c)
                    else:
                        logger.info(f"skip ast.unparse(node)={ast.unparse(node)!r}")
                case _:
                    logger.info(f"skip ast.unparse(node)={ast.unparse(node)!r}")
        return ParsedFileModule(
            name=path.stem, path=path, components=components, dependencies=imports
        )

    def parse_init_module(
        self, module: ast.Module, path: Path
    ) -> ParsedDirectoryModule:
        dir_path = path.parent
        public_component_names = self._extract_all(module)
        return ParsedDirectoryModule(
            name=dir_path.stem,
            path=dir_path,
            public_component_names=public_component_names,
        )

    def _extract_all(self, module: ast.Module) -> list[str]:
        """Extract string values from ``__all__ = [...]`` assignments."""
        for node in module.body:
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return self._parse_all_value(node.value)
        return []

    def _parse_all_value(self, node: ast.expr) -> list[str]:
        if not isinstance(node, (ast.List, ast.Tuple)):
            return []
        names: list[str] = []
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                names.append(elt.value)
        return names
