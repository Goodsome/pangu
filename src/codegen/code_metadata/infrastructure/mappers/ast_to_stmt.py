import ast
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_arguments import AstArguments
from codegen.code_metadata.domain.value_objects.ast_assert import AstAssert
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_aug_assign import AstAugAssign
from codegen.code_metadata.domain.value_objects.ast_break import AstBreak
from codegen.code_metadata.domain.value_objects.ast_continue import AstContinue
from codegen.code_metadata.domain.value_objects.ast_except_handler import (
    AstExceptHandler,
)
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_for import AstFor
from codegen.code_metadata.domain.value_objects.ast_while import AstWhile
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_alias import AstAlias
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_keyword import AstKeyword
from codegen.code_metadata.domain.value_objects.ast_match import AstMatch
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_raise import AstRaise
from codegen.code_metadata.domain.value_objects.ast_return import AstReturn
from codegen.code_metadata.domain.value_objects.ast_try import AstTry
from codegen.code_metadata.domain.value_objects.ast_with import AstWith
from codegen.code_metadata.domain.value_objects.ast_with_item import AstWithItem
from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeVar
from codegen.code_metadata.domain.value_objects.ast_type_param import AstTypeVarTuple
from codegen.code_metadata.domain.value_objects.ast_type_param import AstParamSpec
from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.infrastructure.mappers._convert import binop_from_ast
from codegen.code_metadata.infrastructure.mappers.ast_to_match_pattern import (
    AstToMatchPattern,
)
from codegen.code_metadata.infrastructure.mappers.ast_to_expr import AstToExpr


class AstToStmt:

    @staticmethod
    def to_stmt(node: ast.stmt) -> AstStmt:
        match node:
            case ast.Return():
                return AstToStmt.to_ast_return(node)
            case ast.Raise():
                return AstToStmt.to_ast_raise(node)
            case ast.Assert():
                return AstToStmt.to_ast_assert(node)
            case ast.Pass():
                return AstToStmt.to_ast_pass(node)
            case ast.Break():
                return AstToStmt.to_ast_break(node)
            case ast.Continue():
                return AstToStmt.to_ast_continue(node)
            case ast.With():
                return AstToStmt.to_ast_with(node)
            case ast.AsyncWith():
                return AstToStmt.to_ast_async_with(node)
            case ast.Assign():
                return AstToStmt.to_ast_assign(node)
            case ast.AnnAssign():
                return AstToStmt.to_ast_ann_assign(node)
            case ast.AugAssign():
                return AstToStmt.to_ast_aug_assign(node)
            case ast.For():
                return AstToStmt.to_ast_for(node)
            case ast.While():
                return AstToStmt.to_ast_while(node)
            case ast.If():
                return AstToStmt.to_ast_if(node)
            case ast.Match():
                return AstToStmt.to_ast_match(node)
            case ast.Try():
                return AstToStmt.to_ast_try(node)
            case ast.FunctionDef():
                return AstToStmt.to_ast_function_def(node)
            case ast.AsyncFunctionDef():
                return AstToStmt.to_ast_function_def(node)
            case ast.Import():
                return AstToStmt.to_ast_import(node)
            case ast.ImportFrom():
                return AstToStmt.to_ast_import_from(node)
            case ast.ClassDef():
                return AstToStmt.to_ast_class_def(node)
            case ast.Expr():
                return AstToStmt.to_ast_expr_stmt(node)
            case _:
                raise NotImplementedError(
                    f"Unsupported AST node: node={node!r} \n{ast.unparse(node)}"
                )

    @staticmethod
    def to_ast_return(node: ast.Return) -> AstReturn:
        return AstReturn(value=AstToExpr.to_expr(node.value))

    @staticmethod
    def to_ast_raise(node: ast.Raise) -> AstRaise:
        return AstRaise(
            exc=AstToExpr.to_expr(node.exc), cause=AstToExpr.to_expr(node.cause)
        )

    @staticmethod
    def to_ast_assert(node: ast.Assert) -> AstAssert:
        return AstAssert(
            test=AstToExpr.to_expr(node.test), msg=AstToExpr.to_expr(node.msg)
        )

    @staticmethod
    def to_ast_pass(_node: ast.Pass) -> AstPass:
        return AstPass()

    @staticmethod
    def to_ast_break(_node: ast.Break) -> AstBreak:
        return AstBreak()

    @staticmethod
    def to_ast_continue(_node: ast.Continue) -> AstContinue:
        return AstContinue()

    @staticmethod
    def to_ast_with(node: ast.With) -> AstWith:
        items = [
            AstWithItem(
                context_expr=AstToExpr.to_expr(item.context_expr),
                optional_vars=AstToExpr.to_expr(item.optional_vars),
            )
            for item in node.items
        ]
        body = [AstToStmt.to_stmt(stmt) for stmt in node.body]
        return AstWith(items=items, body=body)

    @staticmethod
    def to_ast_async_with(node: ast.AsyncWith) -> AstWith:
        items = [
            AstWithItem(
                context_expr=AstToExpr.to_expr(item.context_expr),
                optional_vars=AstToExpr.to_expr(item.optional_vars),
            )
            for item in node.items
        ]
        body = [AstToStmt.to_stmt(stmt) for stmt in node.body]
        return AstWith(items=items, body=body, is_async=True)

    @staticmethod
    def to_ast_assign(node: ast.Assign) -> AstAssign:
        targets = [AstToExpr.to_expr(target) for target in node.targets]
        value = AstToExpr.to_expr(node.value)
        return AstAssign(targets=targets, value=value)

    @staticmethod
    def to_ast_ann_assign(node: ast.AnnAssign) -> AstAnnAssign:
        return AstAnnAssign(
            target=AstToExpr.to_expr(node.target),
            annotation=AstToExpr.to_expr(node.annotation),
            value=AstToExpr.to_expr(node.value),
            simple=node.simple,
        )

    @staticmethod
    def to_ast_aug_assign(node: ast.AugAssign) -> AstAugAssign:
        return AstAugAssign(
            target=AstToExpr.to_expr(node.target),
            op=binop_from_ast(node.op),
            value=AstToExpr.to_expr(node.value),
        )

    @staticmethod
    def to_ast_for(node: ast.For) -> AstFor:
        return AstFor(
            target=AstToExpr.to_expr(node.target),
            iter=AstToExpr.to_expr(node.iter),
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            orelse=[AstToStmt.to_stmt(stmt) for stmt in node.orelse],
        )

    @staticmethod
    def to_ast_while(node: ast.While) -> AstWhile:
        return AstWhile(
            test=AstToExpr.to_expr(node.test),
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            orelse=[AstToStmt.to_stmt(stmt) for stmt in node.orelse],
        )

    @staticmethod
    def to_ast_if(node: ast.If) -> AstIf:
        return AstIf(
            test=AstToExpr.to_expr(node.test),
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            orelse=[AstToStmt.to_stmt(stmt) for stmt in node.orelse],
        )

    @staticmethod
    def to_ast_match(node: ast.Match) -> AstMatch:
        cases = [
            AstMatchCase(
                pattern=AstToMatchPattern.to_match_pattern(case.pattern),
                guard=AstToExpr.to_expr(case.guard),
                body=[AstToStmt.to_stmt(stmt) for stmt in case.body],
            )
            for case in node.cases
        ]
        return AstMatch(subject=AstToExpr.to_expr(node.subject), cases=cases)

    @staticmethod
    def to_ast_try(node: ast.Try) -> AstTry:
        handlers = [
            AstExceptHandler(
                type=AstToExpr.to_expr(handler.type) if handler.type else None,
                name=handler.name,
                body=[AstToStmt.to_stmt(stmt) for stmt in handler.body],
            )
            for handler in node.handlers
        ]
        return AstTry(
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            handlers=handlers,
            orelse=[AstToStmt.to_stmt(stmt) for stmt in node.orelse],
            finalbody=[AstToStmt.to_stmt(stmt) for stmt in node.finalbody],
        )

    @staticmethod
    def _to_arg(node: ast.arg) -> Arg:
        annotation = AstToExpr.to_expr(node.annotation)
        return Arg(arg=node.arg, annotation=annotation)

    @staticmethod
    def _to_arguments(node: ast.arguments) -> AstArguments:
        return AstArguments(
            posonlyargs=[AstToStmt._to_arg(a) for a in node.posonlyargs],
            args=[AstToStmt._to_arg(a) for a in node.args],
            vararg=AstToStmt._to_arg(node.vararg) if node.vararg else None,
            kwonlyargs=[AstToStmt._to_arg(a) for a in node.kwonlyargs],
            kw_defaults=[
                AstToExpr.to_expr(d) if d is not None else None
                for d in node.kw_defaults
            ],
            kwarg=AstToStmt._to_arg(node.kwarg) if node.kwarg else None,
            defaults=[AstToExpr.to_expr(d) for d in node.defaults],
        )

    @staticmethod
    def arguments_to_assigns(node: ast.arguments) -> list[AstAssign | AstAnnAssign]:
        if (
            node.posonlyargs
            or node.vararg
            or node.kwonlyargs
            or node.kw_defaults
            or node.kwarg
        ):
            raise ValueError(
                f"Only args and defaults are supported in arguments_to_assigns, ast.dump(node)={ast.dump(node)!r}"
            )
        result: list[AstAssign | AstAnnAssign] = []
        num_args = len(node.args)
        num_defaults = len(node.defaults)
        offset = num_args - num_defaults
        for i, arg in enumerate(node.args):
            target = AstName(id=arg.arg)
            default_index = i - offset
            value = (
                AstToExpr.to_expr(node.defaults[default_index])
                if default_index >= 0
                else None
            )
            if arg.annotation is not None:
                result.append(
                    AstAnnAssign(
                        target=target,
                        annotation=AstToExpr.to_expr(arg.annotation),
                        value=value,
                    )
                )
            else:
                result.append(AstAssign(targets=[target], value=value))
        return result

    @staticmethod
    def to_ast_function_def(node: ast.FunctionDef | ast.AsyncFunctionDef) -> AstFunctionDef:
        arguments = AstToStmt.arguments_to_assigns(node.args)
        return AstFunctionDef(
            lineno=node.lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            name=node.name,
            type_params=[AstToStmt.to_type_param(tp) for tp in node.type_params],
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            decorator_list=[AstToExpr.to_expr(dec) for dec in node.decorator_list],
            returns=AstToExpr.to_expr(node.returns) if node.returns else None,
            type_comment=node.type_comment,
            arguments=arguments,
        )

    @staticmethod
    def to_ast_import(node: ast.Import) -> AstImport:
        names = [AstAlias(name=alias.name, asname=alias.asname) for alias in node.names]
        return AstImport(names=names)

    @staticmethod
    def to_ast_import_from(node: ast.ImportFrom) -> AstImportFrom:
        names = [AstAlias(name=alias.name, asname=alias.asname) for alias in node.names]
        return AstImportFrom(module=node.module, names=names, level=node.level)

    @staticmethod
    def to_type_param(
        node: ast.type_param,
    ) -> AstTypeVar | AstTypeVarTuple | AstParamSpec:
        match node:
            case ast.TypeVar():
                return AstTypeVar(
                    name=node.name,
                    bound=AstToExpr.to_expr(node.bound) if node.bound else None,
                    default_value=(
                        AstToExpr.to_expr(node.default_value)
                        if node.default_value
                        else None
                    ),
                )
            case ast.TypeVarTuple():
                return AstTypeVarTuple(
                    name=node.name,
                    default_value=(
                        AstToExpr.to_expr(node.default_value)
                        if node.default_value
                        else None
                    ),
                )
            case ast.ParamSpec():
                return AstParamSpec(
                    name=node.name,
                    default_value=(
                        AstToExpr.to_expr(node.default_value)
                        if node.default_value
                        else None
                    ),
                )
            case _:
                raise NotImplementedError(f"Unsupported type_param: {type(node)}")

    @staticmethod
    def to_ast_class_def(node: ast.ClassDef) -> AstClassDef:
        bases = [AstToExpr.to_expr(base) for base in node.bases]
        keywords = [
            AstKeyword(arg=kw.arg, value=AstToExpr.to_expr(kw.value))
            for kw in node.keywords
        ]
        type_params = [AstToStmt.to_type_param(tp) for tp in node.type_params]
        body = [AstToStmt.to_stmt(stmt) for stmt in node.body]
        decorator_list = [AstToExpr.to_expr(dec) for dec in node.decorator_list]
        return AstClassDef(
            name=node.name,
            description=ast.get_docstring(node),
            bases=bases,
            keywords=keywords,
            type_params=type_params,
            body=body,
            decorator_list=decorator_list,
        )

    @staticmethod
    def to_ast_expr_stmt(node: ast.Expr) -> AstExprStmt:
        return AstExprStmt(value=AstToExpr.to_expr(node.value))
