import ast
from typing import overload
from codegen.code_metadata.domain.value_objects.ast_expr.ast_await import AstAwait
from codegen.code_metadata.domain.value_objects.ast_expr.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_expr.ast_bin_op import AstBinOp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_bool_op import AstBoolOp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_call import AstCall
from codegen.code_metadata.domain.value_objects.ast_expr.ast_compare import AstCompare
from codegen.code_metadata.domain.value_objects.ast_comprehension import (
    AstComprehension,
)
from codegen.code_metadata.domain.value_objects.ast_expr.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_expr.ast_dict import AstDict
from codegen.code_metadata.domain.value_objects.ast_expr.ast_dict_comp import AstDictComp
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_expr.ast_formatted_value import (
    AstFormattedValue,
)
from codegen.code_metadata.domain.value_objects.ast_expr.ast_generator_exp import AstGeneratorExp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_if_exp import AstIfExp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_joined_str import AstJoinedStr
from codegen.code_metadata.domain.value_objects.ast_expr.ast_lambda import AstLambda
from codegen.code_metadata.domain.value_objects.ast_expr.ast_list import AstList
from codegen.code_metadata.domain.value_objects.ast_expr.ast_list_comp import AstListComp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_expr.ast_named_expr import AstNamedExpr
from codegen.code_metadata.domain.value_objects.ast_expr.ast_set import AstSet
from codegen.code_metadata.domain.value_objects.ast_expr.ast_set_comp import AstSetComp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_slice import AstSlice
from codegen.code_metadata.domain.value_objects.ast_expr.ast_starred import AstStarred
from codegen.code_metadata.domain.value_objects.ast_expr.ast_subscript import AstSubscript
from codegen.code_metadata.domain.value_objects.ast_expr.ast_tuple import AstTuple
from codegen.code_metadata.domain.value_objects.ast_expr.ast_unary_op import AstUnaryOp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_yield import AstYield
from codegen.code_metadata.domain.value_objects.ast_expr.ast_yield_from import AstYieldFrom
from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.lambda_args import LambdaArgs
from codegen.code_metadata.infrastructure.mappers._convert import binop_to_ast
from codegen.code_metadata.infrastructure.mappers._convert import boolop_to_ast
from codegen.code_metadata.infrastructure.mappers._convert import cmpop_to_ast
from codegen.code_metadata.infrastructure.mappers._convert import ctx_to_ast
from codegen.code_metadata.infrastructure.mappers._convert import unaryop_to_ast


class ExprToAst:

    @overload
    @staticmethod
    def to_node(expr: None) -> None: ...

    @overload
    @staticmethod
    def to_node(expr: AstExpr) -> ast.expr: ...

    @staticmethod
    def to_node(expr: AstExpr | None) -> ast.expr | None:
        if expr is None:
            return None
        match expr:
            case AstConstant():
                return ExprToAst.from_constant(expr)
            case AstName():
                return ExprToAst.from_name(expr)
            case AstAttribute():
                return ExprToAst.from_attribute(expr)
            case AstCall():
                return ExprToAst.from_call(expr)
            case AstLambda():
                return ExprToAst.from_lambda(expr)
            case AstIfExp():
                return ExprToAst.from_if_exp(expr)
            case AstBinOp():
                return ExprToAst.from_bin_op(expr)
            case AstBoolOp():
                return ExprToAst.from_bool_op(expr)
            case AstUnaryOp():
                return ExprToAst.from_unary_op(expr)
            case AstCompare():
                return ExprToAst.from_compare(expr)
            case AstJoinedStr():
                return ExprToAst.from_joined_str(expr)
            case AstFormattedValue():
                return ExprToAst.from_formatted_value(expr)
            case AstListComp():
                return ExprToAst.from_list_comp(expr)
            case AstSetComp():
                return ExprToAst.from_set_comp(expr)
            case AstDictComp():
                return ExprToAst.from_dict_comp(expr)
            case AstGeneratorExp():
                return ExprToAst.from_generator_exp(expr)
            case AstSlice():
                return ExprToAst.from_slice(expr)
            case AstStarred():
                return ExprToAst.from_starred(expr)
            case AstSubscript():
                return ExprToAst.from_subscript(expr)
            case AstTuple():
                return ExprToAst.from_tuple(expr)
            case AstList():
                return ExprToAst.from_list(expr)
            case AstSet():
                return ExprToAst.from_set(expr)
            case AstDict():
                return ExprToAst.from_dict(expr)
            case AstYield():
                return ExprToAst.from_yield(expr)
            case AstYieldFrom():
                return ExprToAst.from_yield_from(expr)
            case AstAwait():
                return ExprToAst.from_await(expr)
            case AstNamedExpr():
                return ExprToAst.from_named_expr(expr)
            case _:
                raise NotImplementedError(f"Unsupported AstExpr type: {type(expr)}")

    @staticmethod
    def _to_comprehension(comp: AstComprehension) -> ast.comprehension:
        return ast.comprehension(
            target=ExprToAst.to_node(comp.target),
            iter=ExprToAst.to_node(comp.iter),
            ifs=[ExprToAst.to_node(if_expr) for if_expr in comp.ifs],
            is_async=comp.is_async,
        )

    @staticmethod
    def from_constant(expr: AstConstant) -> ast.Constant:
        return ast.Constant(value=expr.value)

    @staticmethod
    def from_name(expr: AstName) -> ast.Name:
        return ast.Name(id=expr.id, ctx=ast.Load())

    @staticmethod
    def from_attribute(expr: AstAttribute) -> ast.Attribute:
        return ast.Attribute(
            value=ExprToAst.to_node(expr.value), attr=expr.attr, ctx=ast.Load()
        )

    @staticmethod
    def from_call(expr: AstCall) -> ast.Call:
        keywords = [
            ast.keyword(arg=keyword.arg, value=ExprToAst.to_node(keyword.value))
            for keyword in expr.kwargs
        ]
        return ast.Call(
            func=ExprToAst.to_node(expr.func),
            args=[ExprToAst.to_node(arg) for arg in expr.args],
            keywords=keywords,
        )

    @staticmethod
    def from_lambda(expr: AstLambda) -> ast.Lambda:
        return ast.Lambda(
            args=ExprToAst.from_lambda_args(expr.args),
            body=ExprToAst.to_node(expr.body),
        )

    @staticmethod
    def from_lambda_args(args: LambdaArgs) -> ast.arguments:
        return ast.arguments(
            posonlyargs=[ExprToAst.from_arg(a) for a in args.posonlyargs],
            args=[ExprToAst.from_arg(a) for a in args.args],
            vararg=ExprToAst.from_arg(args.vararg) if args.vararg else None,
            kwonlyargs=[ExprToAst.from_arg(a) for a in args.kwonlyargs],
            kw_defaults=[
                ast.parse(d, mode="eval").body if d is not None else None
                for d in args.kw_defaults
            ],
            kwarg=ExprToAst.from_arg(args.kwarg) if args.kwarg else None,
            defaults=[
                ast.parse(d, mode="eval").body if d is not None else None
                for d in args.defaults
            ],
        )

    @staticmethod
    def from_arg(arg: Arg) -> ast.arg:
        annotation = ExprToAst.to_node(arg.annotation)
        return ast.arg(arg=arg.arg, annotation=annotation)

    @staticmethod
    def from_if_exp(expr: AstIfExp) -> ast.IfExp:
        return ast.IfExp(
            test=ExprToAst.to_node(expr.test),
            body=ExprToAst.to_node(expr.body),
            orelse=ExprToAst.to_node(expr.orelse),
        )

    @staticmethod
    def from_bin_op(expr: AstBinOp) -> ast.BinOp:
        return ast.BinOp(
            left=ExprToAst.to_node(expr.left),
            op=binop_to_ast(expr.op),
            right=ExprToAst.to_node(expr.right),
        )

    @staticmethod
    def from_bool_op(expr: AstBoolOp) -> ast.BoolOp:
        return ast.BoolOp(
            op=boolop_to_ast(expr.op),
            values=[ExprToAst.to_node(v) for v in expr.values],
        )

    @staticmethod
    def from_unary_op(expr: AstUnaryOp) -> ast.UnaryOp:
        return ast.UnaryOp(
            op=unaryop_to_ast(expr.op), operand=ExprToAst.to_node(expr.operand)
        )

    @staticmethod
    def from_compare(expr: AstCompare) -> ast.Compare:
        return ast.Compare(
            left=ExprToAst.to_node(expr.left),
            ops=[cmpop_to_ast(op) for op in expr.ops],
            comparators=[ExprToAst.to_node(c) for c in expr.comparators],
        )

    @staticmethod
    def from_joined_str(expr: AstJoinedStr) -> ast.JoinedStr:
        return ast.JoinedStr(values=[ExprToAst.to_node(v) for v in expr.values])

    @staticmethod
    def from_formatted_value(expr: AstFormattedValue) -> ast.FormattedValue:
        return ast.FormattedValue(
            value=ExprToAst.to_node(expr.value),
            conversion=expr.conversion,
            format_spec=ExprToAst.to_node(expr.format_spec),
        )

    @staticmethod
    def from_list_comp(expr: AstListComp) -> ast.ListComp:
        return ast.ListComp(
            elt=ExprToAst.to_node(expr.elt),
            generators=[ExprToAst._to_comprehension(g) for g in expr.generators],
        )

    @staticmethod
    def from_set_comp(expr: AstSetComp) -> ast.SetComp:
        return ast.SetComp(
            elt=ExprToAst.to_node(expr.elt),
            generators=[ExprToAst._to_comprehension(g) for g in expr.generators],
        )

    @staticmethod
    def from_dict_comp(expr: AstDictComp) -> ast.DictComp:
        return ast.DictComp(
            key=ExprToAst.to_node(expr.key),
            value=ExprToAst.to_node(expr.value),
            generators=[ExprToAst._to_comprehension(g) for g in expr.generators],
        )

    @staticmethod
    def from_generator_exp(expr: AstGeneratorExp) -> ast.GeneratorExp:
        return ast.GeneratorExp(
            elt=ExprToAst.to_node(expr.elt),
            generators=[ExprToAst._to_comprehension(g) for g in expr.generators],
        )

    @staticmethod
    def from_slice(expr: AstSlice) -> ast.Slice:
        return ast.Slice(
            lower=ExprToAst.to_node(expr.lower),
            upper=ExprToAst.to_node(expr.upper),
            step=ExprToAst.to_node(expr.step),
        )

    @staticmethod
    def from_starred(expr: AstStarred) -> ast.Starred:
        return ast.Starred(
            value=ExprToAst.to_node(expr.value), ctx=ctx_to_ast(expr.ctx)
        )

    @staticmethod
    def from_subscript(expr: AstSubscript) -> ast.Subscript:
        return ast.Subscript(
            value=ExprToAst.to_node(expr.value),
            slice=ExprToAst.to_node(expr.slice),
            ctx=ast.Load(),
        )

    @staticmethod
    def from_tuple(expr: AstTuple) -> ast.Tuple:
        return ast.Tuple(elts=[ExprToAst.to_node(e) for e in expr.elts], ctx=ast.Load())

    @staticmethod
    def from_list(expr: AstList) -> ast.List:
        return ast.List(elts=[ExprToAst.to_node(e) for e in expr.elts], ctx=ast.Load())

    @staticmethod
    def from_set(expr: AstSet) -> ast.Set:
        return ast.Set(elts=[ExprToAst.to_node(e) for e in expr.elts])

    @staticmethod
    def from_dict(expr: AstDict) -> ast.Dict:
        return ast.Dict(
            keys=[ExprToAst.to_node(k) for k in expr.keys],
            values=[ExprToAst.to_node(v) for v in expr.values],
        )

    @staticmethod
    def from_yield(expr: AstYield) -> ast.Yield:
        return ast.Yield(value=ExprToAst.to_node(expr.value))

    @staticmethod
    def from_yield_from(expr: AstYieldFrom) -> ast.YieldFrom:
        return ast.YieldFrom(value=ExprToAst.to_node(expr.value))

    @staticmethod
    def from_await(expr: AstAwait) -> ast.Await:
        return ast.Await(value=ExprToAst.to_node(expr.value))

    @staticmethod
    def from_named_expr(expr: AstNamedExpr) -> ast.NamedExpr:
        return ast.NamedExpr(
            target=ast.Name(id=expr.target.id, ctx=ast.Store()),
            value=ExprToAst.to_node(expr.value),
        )
