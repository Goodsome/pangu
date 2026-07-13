import ast
from typing import overload
from code_dom.domain.value_objects.ast_expr import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_attribute import (
    AstAttribute,
)
from code_dom.domain.value_objects.ast_expr.ast_bin_op import AstBinOp
from code_dom.domain.value_objects.ast_expr.ast_bool_op import AstBoolOp
from code_dom.domain.value_objects.ast_expr.ast_call import AstCall
from code_dom.domain.value_objects.ast_expr.ast_compare import AstCompare
from code_dom.domain.value_objects.ast_expr.ast_comprehension import (
    AstComprehension,
)
from code_dom.domain.value_objects.ast_expr.ast_constant import AstConstant
from code_dom.domain.value_objects.ast_expr.ast_dict import AstDict
from code_dom.domain.value_objects.ast_expr.ast_dict_comp import (
    AstDictComp,
)
from code_dom.domain.value_objects.ast_expr.ast_formatted_value import (
    AstFormattedValue,
)
from code_dom.domain.value_objects.ast_expr.ast_generator_exp import (
    AstGeneratorExp,
)
from code_dom.domain.value_objects.ast_expr.ast_if_exp import AstIfExp
from code_dom.domain.value_objects.ast_expr.ast_joined_str import (
    AstJoinedStr,
)
from code_dom.domain.value_objects.ast_expr.ast_keyword import AstKeyword
from code_dom.domain.value_objects.ast_expr.ast_lambda import (
    AstLambda,
    LambdaArgs,
    Arg,
)
from code_dom.domain.value_objects.ast_expr.ast_list import AstList
from code_dom.domain.value_objects.ast_expr.ast_list_comp import (
    AstListComp,
)
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_expr.ast_named_expr import (
    AstNamedExpr,
)
from code_dom.domain.value_objects.ast_expr.ast_set import AstSet
from code_dom.domain.value_objects.ast_expr.ast_set_comp import AstSetComp
from code_dom.domain.value_objects.ast_expr.ast_slice import AstSlice
from code_dom.domain.value_objects.ast_expr.ast_starred import AstStarred
from code_dom.domain.value_objects.ast_expr.ast_subscript import (
    AstSubscript,
)
from code_dom.domain.value_objects.ast_expr.ast_tuple import AstTuple
from code_dom.domain.value_objects.ast_expr.ast_unary_op import AstUnaryOp
from code_dom.domain.value_objects.ast_expr.ast_yield import AstYield
from code_dom.domain.value_objects.ast_expr.ast_await import AstAwait
from code_dom.domain.value_objects.ast_expr.ast_yield_from import (
    AstYieldFrom,
)
from code_dom.infrastructure.mappers._convert import binop_from_ast
from code_dom.infrastructure.mappers._convert import boolop_from_ast
from code_dom.infrastructure.mappers._convert import cmpop_from_ast
from code_dom.infrastructure.mappers._convert import ctx_from_ast
from code_dom.infrastructure.mappers._convert import unaryop_from_ast


class AstToExpr:
    @overload
    @staticmethod
    def to_expr(node: None) -> None: ...

    @overload
    @staticmethod
    def to_expr(node: ast.expr) -> AstExprBase: ...

    @staticmethod
    def to_expr(node: ast.expr | None) -> AstExprBase | None:
        if node is None:
            return None
        match node:
            case ast.Constant():
                return AstToExpr.to_ast_constant(node)
            case ast.Name():
                return AstToExpr.to_ast_name(node)
            case ast.Attribute():
                return AstToExpr.to_ast_attribute(node)
            case ast.Call():
                return AstToExpr.to_ast_call(node)
            case ast.Lambda():
                return AstToExpr.to_ast_lambda(node)
            case ast.IfExp():
                return AstToExpr.to_ast_if_exp(node)
            case ast.BinOp():
                return AstToExpr.to_ast_bin_op(node)
            case ast.BoolOp():
                return AstToExpr.to_ast_bool_op(node)
            case ast.UnaryOp():
                return AstToExpr.to_ast_unary_op(node)
            case ast.Compare():
                return AstToExpr.to_ast_compare(node)
            case ast.JoinedStr():
                return AstToExpr.to_ast_joined_str(node)
            case ast.FormattedValue():
                return AstToExpr.to_ast_formatted_value(node)
            case ast.ListComp():
                return AstToExpr.to_ast_list_comp(node)
            case ast.SetComp():
                return AstToExpr.to_ast_set_comp(node)
            case ast.DictComp():
                return AstToExpr.to_ast_dict_comp(node)
            case ast.GeneratorExp():
                return AstToExpr.to_ast_generator_exp(node)
            case ast.Slice():
                return AstToExpr.to_ast_slice(node)
            case ast.Starred():
                return AstToExpr.to_ast_starred(node)
            case ast.Subscript():
                return AstToExpr.to_ast_subscript(node)
            case ast.Tuple():
                return AstToExpr.to_ast_tuple(node)
            case ast.List():
                return AstToExpr.to_ast_list(node)
            case ast.Set():
                return AstToExpr.to_ast_set(node)
            case ast.Dict():
                return AstToExpr.to_ast_dict(node)
            case ast.Yield():
                return AstToExpr.to_ast_yield(node)
            case ast.YieldFrom():
                return AstToExpr.to_ast_yield_from(node)
            case ast.Await():
                return AstToExpr.to_ast_await(node)
            case ast.NamedExpr():
                return AstToExpr.to_ast_named_expr(node)
            case _:
                raise NotImplementedError(
                    f"Unsupported node type: {type(node)}, ast.unparse(node)={ast.unparse(node)!r}"
                )

    @staticmethod
    def to_ast_constant(node: ast.Constant) -> AstConstant:
        return AstConstant(value=node.value)

    @staticmethod
    def to_ast_name(node: ast.Name) -> AstName:
        return AstName(id=node.id)

    @staticmethod
    def to_ast_attribute(node: ast.Attribute) -> AstAttribute:
        return AstAttribute(value=AstToExpr.to_expr(node.value), attr=node.attr)

    @staticmethod
    def to_ast_call(node: ast.Call) -> AstCall:
        kwargs = [
            AstKeyword(arg=kw.arg, value=AstToExpr.to_expr(kw.value))
            for kw in node.keywords
        ]
        return AstCall(
            func=AstToExpr.to_expr(node.func),
            args=[AstToExpr.to_expr(arg) for arg in node.args],
            kwargs=kwargs,
        )

    @staticmethod
    def to_ast_lambda(node: ast.Lambda) -> AstLambda:
        return AstLambda(
            args=AstToExpr.to_lambda_args(node.args), body=AstToExpr.to_expr(node.body)
        )

    @staticmethod
    def to_lambda_args(node: ast.arguments) -> LambdaArgs:
        return LambdaArgs(
            posonlyargs=[AstToExpr.to_arg(a) for a in node.posonlyargs],
            args=[AstToExpr.to_arg(a) for a in node.args],
            vararg=AstToExpr.to_arg(node.vararg) if node.vararg else None,
            kwonlyargs=[AstToExpr.to_arg(a) for a in node.kwonlyargs],
            kw_defaults=[
                ast.unparse(d) if d is not None else None for d in node.kw_defaults
            ],
            kwarg=AstToExpr.to_arg(node.kwarg) if node.kwarg else None,
            defaults=[ast.unparse(d) if d is not None else None for d in node.defaults],
        )

    @staticmethod
    def to_arg(node: ast.arg) -> Arg:
        annotation = AstToExpr.to_expr(node.annotation)
        return Arg(arg=node.arg, annotation=annotation)

    @staticmethod
    def to_ast_if_exp(node: ast.IfExp) -> AstIfExp:
        return AstIfExp(
            test=AstToExpr.to_expr(node.test),
            body=AstToExpr.to_expr(node.body),
            orelse=AstToExpr.to_expr(node.orelse),
        )

    @staticmethod
    def to_ast_bin_op(node: ast.BinOp) -> AstBinOp:
        return AstBinOp(
            left=AstToExpr.to_expr(node.left),
            op=binop_from_ast(node.op),
            right=AstToExpr.to_expr(node.right),
        )

    @staticmethod
    def to_ast_bool_op(node: ast.BoolOp) -> AstBoolOp:
        return AstBoolOp(
            op=boolop_from_ast(node.op),
            values=[AstToExpr.to_expr(value) for value in node.values],
        )

    @staticmethod
    def to_ast_unary_op(node: ast.UnaryOp) -> AstUnaryOp:
        return AstUnaryOp(
            op=unaryop_from_ast(node.op), operand=AstToExpr.to_expr(node.operand)
        )

    @staticmethod
    def to_ast_compare(node: ast.Compare) -> AstCompare:
        return AstCompare(
            left=AstToExpr.to_expr(node.left),
            ops=[cmpop_from_ast(op) for op in node.ops],
            comparators=[AstToExpr.to_expr(comp) for comp in node.comparators],
        )

    @staticmethod
    def to_ast_joined_str(node: ast.JoinedStr) -> AstJoinedStr:
        return AstJoinedStr(values=[AstToExpr.to_expr(value) for value in node.values])

    @staticmethod
    def to_ast_formatted_value(node: ast.FormattedValue) -> AstFormattedValue:
        return AstFormattedValue(
            value=AstToExpr.to_expr(node.value),
            conversion=node.conversion,
            format_spec=AstToExpr.to_expr(node.format_spec)
            if node.format_spec
            else None,
        )

    @staticmethod
    def to_ast_list_comp(node: ast.ListComp) -> AstListComp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstListComp(elt=AstToExpr.to_expr(node.elt), generators=generators)

    @staticmethod
    def to_ast_set_comp(node: ast.SetComp) -> AstSetComp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstSetComp(elt=AstToExpr.to_expr(node.elt), generators=generators)

    @staticmethod
    def to_ast_dict_comp(node: ast.DictComp) -> AstDictComp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstDictComp(
            key=AstToExpr.to_expr(node.key),
            value=AstToExpr.to_expr(node.value),
            generators=generators,
        )

    @staticmethod
    def to_ast_generator_exp(node: ast.GeneratorExp) -> AstGeneratorExp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstGeneratorExp(elt=AstToExpr.to_expr(node.elt), generators=generators)

    @staticmethod
    def to_ast_slice(node: ast.Slice) -> AstSlice:
        return AstSlice(
            lower=AstToExpr.to_expr(node.lower) if node.lower else None,
            upper=AstToExpr.to_expr(node.upper) if node.upper else None,
            step=AstToExpr.to_expr(node.step) if node.step else None,
        )

    @staticmethod
    def to_ast_starred(node: ast.Starred) -> AstStarred:
        return AstStarred(
            value=AstToExpr.to_expr(node.value), ctx=ctx_from_ast(node.ctx)
        )

    @staticmethod
    def to_ast_subscript(node: ast.Subscript) -> AstSubscript:
        return AstSubscript(
            value=AstToExpr.to_expr(node.value), slice=AstToExpr.to_expr(node.slice)
        )

    @staticmethod
    def to_ast_tuple(node: ast.Tuple) -> AstTuple:
        return AstTuple(elts=[AstToExpr.to_expr(elt) for elt in node.elts])

    @staticmethod
    def to_ast_list(node: ast.List) -> AstList:
        return AstList(elts=[AstToExpr.to_expr(elt) for elt in node.elts])

    @staticmethod
    def to_ast_set(node: ast.Set) -> AstSet:
        return AstSet(elts=[AstToExpr.to_expr(elt) for elt in node.elts])

    @staticmethod
    def to_ast_dict(node: ast.Dict) -> AstDict:
        return AstDict(
            keys=[AstToExpr.to_expr(key) for key in node.keys],
            values=[AstToExpr.to_expr(value) for value in node.values],
        )

    @staticmethod
    def to_ast_yield(node: ast.Yield) -> AstYield:
        return AstYield(value=AstToExpr.to_expr(node.value) if node.value else None)

    @staticmethod
    def to_ast_yield_from(node: ast.YieldFrom) -> AstYieldFrom:
        return AstYieldFrom(value=AstToExpr.to_expr(node.value))

    @staticmethod
    def to_ast_await(node: ast.Await) -> AstAwait:
        return AstAwait(value=AstToExpr.to_expr(node.value))

    @staticmethod
    def to_ast_named_expr(node: ast.NamedExpr) -> AstNamedExpr:
        return AstNamedExpr(
            target=AstToExpr.to_ast_name(node.target),
            value=AstToExpr.to_expr(node.value),
        )
