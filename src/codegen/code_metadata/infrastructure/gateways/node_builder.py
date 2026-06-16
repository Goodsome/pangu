from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import override
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.services.ast_visitor import AstVisitor
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import FunctionNode
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.code_node import ParameterNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.infrastructure.gateways.utils import get_import_from_module


@dataclass
class NodeBuilder(AstVisitor):
    root_path: Path
    fqn_factory: FqnFactory
    node_registery: NodeRegistry
    imports: set[str] = field(default_factory=set)
    node_stack: list[CodeNode] = field(default_factory=list)
    _current_module: ModuleNode | None = None
    _in_function_body: bool = False

    @property
    def current_module(self) -> ModuleNode:
        if self._current_module is None:
            raise ValueError(f"{self._current_module} is None")
        return self._current_module

    @property
    def current_node(self) -> CodeNode:
        if not self.node_stack:
            raise ValueError(f"{self.node_stack} is None")
        return self.node_stack[-1]

    def build(self, code_documents: list[CodeDocument]) -> None:
        for doc in code_documents:
            self._build_module_node(doc)

    def _add_node(self, dto: CodeNode) -> None:
        self.node_registery.add_node(dto)

    def _build_module_by_path(self, path: Path) -> ModuleNode:
        module_fqn = self.fqn_factory.build_module_fqn(path)
        node = ModuleNode(id=module_fqn, name=module_fqn.rsplit(".", maxsplit=1)[-1])
        self._add_node(node)
        return node

    def _find_or_create_module(self, path: Path) -> ModuleNode:
        module_fqn = self.fqn_factory.build_module_fqn(path)
        node = self.node_registery.find_node(module_fqn)
        if node:
            assert isinstance(node, ModuleNode)
            return node
        node = self._build_module_by_path(path)
        return node

    def _ensure_parent_module(self, module: ModuleNode) -> None:
        module_path = module.get_physical_path()
        if module_path.with_suffix("") == self.root_path:
            return
        assert len(module_path.parts) >= len(
            self.root_path.parts
        ), f"module_path={module_path!r} not under self.root_path={self.root_path!r}"
        parent_path = module_path.parent
        parent = self._find_or_create_module(parent_path)
        parent.is_package = True
        parent.contains(module)

    def _build_module_node(self, code_document: CodeDocument) -> ModuleNode:
        path = code_document.physical_path
        node = self._find_or_create_module(path)
        node.description = code_document.description
        node.is_package = path.name == "__init__.py"
        self._ensure_parent_module(node)
        self._current_module = node
        self.node_stack.append(node)
        self.visit(code_document.body)
        return node

    @override
    def visit_ast_import(self, node: AstImport):
        for name in node.names:
            self.imports.add(name.name)
        return super().visit_ast_import(node)

    @override
    def visit_ast_import_from(self, node: AstImportFrom):
        from_module = get_import_from_module(
            origin_module=node.module, level=node.level, module_node=self.current_module
        )
        self.imports.add(from_module)
        return super().visit_ast_import_from(node)

    @override
    def visit_ast_expr_stmt(self, node: AstExprStmt):
        if isinstance(self.current_node, ModuleNode):
            self.current_node.exprs.append(node.value)
        return super().visit_ast_expr_stmt(node)

    @override
    def visit_ast_class_def(self, node: AstClassDef):
        assert isinstance(self.current_node, ModuleNode)
        class_fqn = Fqn(f"{self.current_node.id}::{node.name}")
        class_node = ClassNode(
            id=class_fqn,
            name=node.name,
            description=node.description,
            decorator_list=node.decorator_list,
            bases=node.bases,
            type_params=node.type_params,
        )
        self._add_node(class_node)
        self.current_node.defines(class_node)
        self.node_stack.append(class_node)
        super().visit_ast_class_def(node)
        self.node_stack.pop()

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        parent_node = self.current_node
        _func_fqn = f"{parent_node.id}::{node.name}"
        check_reachable = True
        if node.is_overload:
            _func_fqn = f"{_func_fqn}<overload_{node.lineno}>"
            check_reachable = False
        elif node.is_setter_property:
            _func_fqn = f"{_func_fqn}<setter>"
            check_reachable = False
        elif node.is_deleter_property:
            _func_fqn = f"{_func_fqn}<deleter>"
            check_reachable = False
        elif node.is_expression_property:
            _func_fqn = f"{_func_fqn}<expression>"
            check_reachable = False
        elif node.is_override:
            check_reachable = False
        if node.name.startswith("__"):
            check_reachable = False
        fqn = Fqn(_func_fqn)
        match parent_node:
            case ClassNode():
                func_node = MethodNode(
                    id=fqn,
                    name=node.name,
                    decorator_list=node.decorator_list,
                    returns=node.returns,
                    body=node.body,
                    is_async=node.is_async,
                    check_reachable=check_reachable,
                )
                parent_node.defines(func_node)
            case ModuleNode():
                func_node = FunctionNode(
                    id=fqn,
                    name=node.name,
                    decorator_list=node.decorator_list,
                    returns=node.returns,
                    body=node.body,
                    is_async=node.is_async,
                )
                parent_node.defines(func_node)
            case MethodNode():
                return
            case _:
                raise NotImplementedError(f"parent_node={parent_node!r}")
        self._add_node(func_node)
        self.node_stack.append(func_node)
        self.visit(node.decorator_list)
        for arg in node.arguments:
            self.visit(arg)
        self._in_function_body = True
        self.visit(node.body)
        self._in_function_body = False
        if node.returns is not None:
            self.visit(node.returns)
        self.node_stack.pop()

    @override
    def visit_ast_assign(self, node: AstAssign) -> None:
        target = node.target
        self._create_variable_node(
            target=target, annotation=node.annotation, value=node.value
        )
        return super().visit_ast_assign(node)

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        target = node.target
        self._create_variable_node(
            target=target, annotation=node.annotation, value=node.value
        )
        return super().visit_ast_ann_assign(node)

    def _create_variable_node(
        self,
        target: AstExpr,
        annotation: AstExpr | None = None,
        value: AstExpr | None = None,
    ) -> None:
        if self._in_function_body:
            return
        if not isinstance(target, AstName):
            return
        assert isinstance(
            self.current_node, (ModuleNode, ClassNode, FunctionNode, MethodNode)
        )
        name = target.id
        var_fqn = Fqn(f"{self.current_node.id}::{name}")
        match self.current_node:
            case ModuleNode() | ClassNode():
                node = VariableNode(
                    id=var_fqn, name=name, annotation=annotation, value=value
                )
                self.current_node.defines(node)
            case FunctionNode() | MethodNode():
                node = ParameterNode(
                    id=var_fqn, name=name, annotation=annotation, value=value
                )
                self.current_node.defines(node)
        self._add_node(node)
