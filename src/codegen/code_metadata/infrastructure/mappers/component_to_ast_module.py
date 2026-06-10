import ast
from collections import defaultdict
from dataclasses import dataclass
from typing_extensions import overload
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.aggregates.module import FileModule
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.component import UnionComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.services.translate_reference import TranslateReference
from codegen.code_metadata.domain.value_objects.call_expr import CallExpr
from codegen.code_metadata.domain.value_objects.constant_expr import ConstantExpr
from codegen.code_metadata.domain.value_objects.dict_expr import DictExpr
from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.lambda_expr import LambdaExpr
from codegen.code_metadata.domain.value_objects.module_dependency import (
    ModuleDependency,
)
from codegen.code_metadata.domain.value_objects.reference_expr import ReferenceExpr
from codegen.code_metadata.domain.value_objects.sequence_expr import SequenceExpr
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.code_metadata.infrastructure.mappers.expr_to_ast import ExprToAst
from codegen.code_metadata.infrastructure.mappers.stmt_to_ast import StmtToAst
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class ComponentToAstModule:
    resolver: TranslateReference
    component_policy_factory: ComponentPolicyFactory

    def module_to_ast(self, module: FileModule) -> ast.Module:
        body: list[ast.stmt] = []
        type_checkings: list[ast.stmt] = []
        for dependency in module.dependencies:
            if dependency.type_checking:
                type_checkings.append(self.module_dependency_to_ast(dependency))
            else:
                body.append(self.module_dependency_to_ast(dependency))
        if type_checkings:
            body.append(
                ast.If(
                    test=ast.Name(id="TYPE_CHECKING"), body=type_checkings, orelse=[]
                )
            )
        for component in module.components:
            body.append(self.component_to_ast(component))
        return ast.Module(body=body)

    def module_dependency_to_ast(
        self, dependency: ModuleDependency
    ) -> ast.ImportFrom | ast.Import:
        module = self.resolver.resolve_reference(dependency.module)
        if dependency.component:
            component = self.resolver.resolve_reference(dependency.component)
            node = ast.ImportFrom(
                module=module, names=[ast.alias(name=component, asname=None)], level=0
            )
        else:
            node = ast.Import(names=[ast.alias(name=module, asname=None)])
        return node

    def component_to_ast(self, component: Component) -> ast.stmt:
        match component:
            case ClassComponent():
                return self.to_ast_class(component)
            case UnionComponent():
                return self.union_component_to_ast(component)

    def union_component_to_ast(self, component: UnionComponent) -> ast.Assign:
        member_names = [
            ast.Name(id=self.resolver.resolve_reference(member_id))
            for member_id in component.members
        ]
        union_expr: ast.expr = member_names[0]
        for name_node in member_names[1:]:
            union_expr = ast.BinOp(left=union_expr, op=ast.BitOr(), right=name_node)
        field_call = ast.Call(
            func=ast.Name(id="Field"),
            args=[],
            keywords=[
                ast.keyword(
                    arg="discriminator",
                    value=ast.Constant(value=component.discriminator),
                )
            ],
        )
        annotated_subscript = ast.Subscript(
            value=ast.Name(id="Annotated"),
            slice=ast.Tuple(elts=[union_expr, field_call], ctx=ast.Load()),
            ctx=ast.Load(),
        )
        return ast.Assign(
            targets=[ast.Name(id=component.name, ctx=ast.Store())],
            value=annotated_subscript,
        )

    def to_ast_module(self, component: Component) -> ast.Module:
        import_froms = self._get_import_froms(component)
        body: list[ast.stmt] = [*import_froms]
        match component:
            case ClassComponent():
                body.append(self.to_ast_class(component))
            case UnionComponent():
                body.append(self.union_component_to_ast(component))
        module = ast.Module(body=body)
        return module

    def _get_import_froms(self, component: Component) -> list[ast.ImportFrom]:
        collect_module_names: dict[str, set[str]] = defaultdict(set)
        for dep_id in component.get_dependencies():
            dc = self.resolver.get_component(dep_id)
            policy = self.component_policy_factory.get_policy(component_type=dc.type)
            module = dc.get_import_module(policy)
            collect_module_names[module].add(dc.name)
        result: list[ast.ImportFrom] = []
        for module, names in sorted(collect_module_names.items()):
            import_from = ast.ImportFrom(
                module=module, names=[ast.alias(name=name) for name in names], level=0
            )
            result.append(import_from)
        return result

    @overload
    def type_to_ast_expr(self, type_: TypeDef) -> ast.expr: ...

    @overload
    def type_to_ast_expr(self, type_: None) -> None: ...

    def type_to_ast_expr(self, type_: TypeDef | None) -> ast.expr | None:
        if type_ is None:
            return None
        name = self.resolver.resolve_reference_target(type_.origin)
        if name == PythonBuiltinType.NONE:
            return ast.Constant(value=None, kind=None)
        elif name == PythonBuiltinType.UNION:
            if len(type_.args) == 1:
                return self.type_to_ast_expr(type_.args[0])
            elif len(type_.args) == 2:
                return ast.BinOp(
                    left=self.type_to_ast_expr(type_.args[0]),
                    right=self.type_to_ast_expr(type_.args[1]),
                    op=ast.BitOr(),
                )
            else:
                remain_type = TypeDef(origin=type_.origin, args=type_.args[1:])
                return ast.BinOp(
                    left=self.type_to_ast_expr(type_.args[0]),
                    right=self.type_to_ast_expr(remain_type),
                    op=ast.BitOr(),
                )
        base_node = ast.Name(id=name, ctx=ast.Load())
        if not type_.args:
            return base_node
        if len(type_.args) == 1:
            slice_node = self.type_to_ast_expr(type_.args[0])
        else:
            slice_node = ast.Tuple(
                elts=[self.type_to_ast_expr(arg) for arg in type_.args], ctx=ast.Load()
            )
        return ast.Subscript(value=base_node, slice=slice_node, ctx=ast.Load())

    @overload
    def expr_to_ast_expr(self, expr: None) -> None: ...

    @overload
    def expr_to_ast_expr(self, expr: ExprDef) -> ast.expr: ...

    def expr_to_ast_expr(self, expr: ExprDef | None) -> ast.expr | None:
        if expr is None:
            return None
        match expr.kind:
            case ExprKind.CONSTANT:
                return self.map_constant(expr)
            case ExprKind.REFERENCE:
                return self.map_reference(expr)
            case ExprKind.CALL:
                return self.map_call(expr)
            case ExprKind.DICT:
                return self.map_dict(expr)
            case ExprKind.SEQUENCE:
                return self.map_sequence(expr)
            case ExprKind.LAMBDA:
                return self.map_lambda(expr)
            case _:
                raise ValueError(f"Unsupported expression kind: {expr.kind}")

    def map_constant(self, expr: ConstantExpr) -> ast.Constant:
        return ast.Constant(value=expr.value)

    def map_reference(self, expr: ReferenceExpr) -> ast.Name | ast.Attribute:
        if expr.source is None:
            name = self.resolver.resolve_reference_target(expr.target)
            return ast.Name(id=name)
        else:
            source_expr = self.expr_to_ast_expr(expr.source)
            if not isinstance(expr.source, ReferenceExpr):
                raise ValueError("Expected source expression to be an attribute")
            name = self.resolver.resolve_reference_target(target=expr.target)
            return ast.Attribute(value=source_expr, attr=name)

    def map_call(self, expr: CallExpr) -> ast.Call:
        func = self.expr_to_ast_expr(expr.callee)
        args = [self.expr_to_ast_expr(arg) for arg in expr.args]
        keywords: list[ast.keyword] = []
        for k, v in expr.kwargs.items():
            if k == "**":
                arg = None
            else:
                arg = k
            keywords.append(ast.keyword(arg=arg, value=self.expr_to_ast_expr(v)))
        return ast.Call(func=func, args=args, keywords=keywords)

    def map_sequence(self, expr: SequenceExpr) -> ast.List | ast.Tuple | ast.Set:
        elts = [self.expr_to_ast_expr(elt) for elt in expr.elements]
        ast_container = {"list": ast.List, "tuple": ast.Tuple, "set": ast.Set}[
            expr.container_type
        ]
        return ast_container(elts=elts)

    def map_dict(self, expr: DictExpr) -> ast.Dict:
        keys: list[ast.expr | None] = []
        values: list[ast.expr] = []
        for item in expr.items:
            keys.append(
                self.expr_to_ast_expr(item.key) if item.key is not None else None
            )
            values.append(self.expr_to_ast_expr(item.value))
        return ast.Dict(keys=keys, values=values)

    def map_lambda(self, expr: LambdaExpr) -> ast.Lambda:
        args = ast.arguments(
            args=[ast.arg(arg=arg) for arg in expr.params],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )
        body = self.expr_to_ast_expr(expr.body)
        return ast.Lambda(args=args, body=body)

    def attribute_to_ast_assign(
        self, attribute: Attribute
    ) -> ast.AnnAssign | ast.Assign | ast.Expr:
        target = ast.Name(id=attribute.name, ctx=ast.Store())
        annotation = self.type_to_ast_expr(attribute.type)
        value = ExprToAst.to_node(attribute.value_v2)
        if annotation:
            return ast.AnnAssign(
                target=target, annotation=annotation, value=value, simple=1
            )
        elif value is not None:
            return ast.Assign(targets=[target], value=value)
        else:
            return ast.Expr(value=ast.Name(id=attribute.name, ctx=ast.Load()))

    def attributes_to_arguments(self, attributes: list[Attribute]) -> ast.arguments:
        args: list[ast.arg] = []
        defaults: list[ast.expr] = []
        for attribute in attributes:
            args.append(
                ast.arg(
                    arg=attribute.name, annotation=self.type_to_ast_expr(attribute.type)
                )
            )
            value = self.expr_to_ast_expr(attribute.value)
            if value:
                defaults.append(value)
        return ast.arguments(args=args, defaults=defaults)

    def to_ast(self, behavior: Behavior) -> ast.FunctionDef:
        body: list[ast.stmt] = []
        if behavior.description:
            body.append(ast.Expr(value=ast.Constant(value=behavior.description)))
        for b in behavior.body:
            body.append(StmtToAst.to_node(b))
        arguments = self.attributes_to_arguments(behavior.inputs)
        returns = self.type_to_ast_expr(behavior.output)
        return ast.FunctionDef(
            name=behavior.name, args=arguments, body=body, returns=returns
        )

    def to_ast_class(self, component: ClassComponent) -> ast.ClassDef:
        body: list[ast.stmt] = []
        if component.description:
            body.append(ast.Expr(value=ast.Constant(value=component.description)))
        for attribute in component.attributes:
            body.append(self.attribute_to_ast_assign(attribute))
        for behavior in component.behaviors:
            body.append(self.to_ast(behavior))
        if not body:
            body.append(ast.Expr(ast.Constant(value=...)))
        bases = [self.type_to_ast_expr(t) for t in component.bases]
        class_def = ast.ClassDef(
            name=component.name, bases=bases, keywords=[], body=body
        )
        return class_def
