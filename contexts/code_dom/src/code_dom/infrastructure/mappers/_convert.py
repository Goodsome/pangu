"""Conversion functions between ast.* types and internal domain enums/structures."""

import ast
from code_dom.domain.enums.bin_op import BinOp
from code_dom.domain.enums.bool_op import BoolOp
from code_dom.domain.enums.cmp_op import CmpOp
from code_dom.domain.enums.expr_context import ExprContext
from code_dom.domain.enums.unary_op import UnaryOp

_AST_BINOP_TO_DOMAIN: dict[type[ast.operator], BinOp] = {
    ast.Add: BinOp.ADD,
    ast.Sub: BinOp.SUB,
    ast.Mult: BinOp.MULT,
    ast.Div: BinOp.DIV,
    ast.FloorDiv: BinOp.FLOOR_DIV,
    ast.Mod: BinOp.MOD,
    ast.Pow: BinOp.POW,
    ast.LShift: BinOp.LSHIFT,
    ast.RShift: BinOp.RSHIFT,
    ast.BitOr: BinOp.BIT_OR,
    ast.BitXor: BinOp.BIT_XOR,
    ast.BitAnd: BinOp.BIT_AND,
    ast.MatMult: BinOp.MAT_MULT,
}
_DOMAIN_BINOP_TO_AST: dict[BinOp, ast.operator] = {
    v: k() for k, v in _AST_BINOP_TO_DOMAIN.items()
}


def binop_from_ast(op: ast.operator) -> BinOp:
    return _AST_BINOP_TO_DOMAIN[type(op)]


def binop_to_ast(op: BinOp) -> ast.operator:
    return _DOMAIN_BINOP_TO_AST[op]


_AST_BOOLOP_TO_DOMAIN: dict[type[ast.boolop], BoolOp] = {
    ast.And: BoolOp.AND,
    ast.Or: BoolOp.OR,
}
_DOMAIN_BOOLOP_TO_AST: dict[BoolOp, ast.boolop] = {
    v: k() for k, v in _AST_BOOLOP_TO_DOMAIN.items()
}


def boolop_from_ast(op: ast.boolop) -> BoolOp:
    return _AST_BOOLOP_TO_DOMAIN[type(op)]


def boolop_to_ast(op: BoolOp) -> ast.boolop:
    return _DOMAIN_BOOLOP_TO_AST[op]


_AST_UNARYOP_TO_DOMAIN: dict[type[ast.unaryop], UnaryOp] = {
    ast.Not: UnaryOp.NOT,
    ast.Invert: UnaryOp.INVERT,
    ast.UAdd: UnaryOp.UADD,
    ast.USub: UnaryOp.USUB,
}
_DOMAIN_UNARYOP_TO_AST: dict[UnaryOp, ast.unaryop] = {
    v: k() for k, v in _AST_UNARYOP_TO_DOMAIN.items()
}


def unaryop_from_ast(op: ast.unaryop) -> UnaryOp:
    return _AST_UNARYOP_TO_DOMAIN[type(op)]


def unaryop_to_ast(op: UnaryOp) -> ast.unaryop:
    return _DOMAIN_UNARYOP_TO_AST[op]


_AST_CMPOP_TO_DOMAIN: dict[type[ast.cmpop], CmpOp] = {
    ast.Eq: CmpOp.EQ,
    ast.NotEq: CmpOp.NOT_EQ,
    ast.Lt: CmpOp.LT,
    ast.LtE: CmpOp.LT_E,
    ast.Gt: CmpOp.GT,
    ast.GtE: CmpOp.GT_E,
    ast.Is: CmpOp.IS,
    ast.IsNot: CmpOp.IS_NOT,
    ast.In: CmpOp.IN,
    ast.NotIn: CmpOp.NOT_IN,
}
_DOMAIN_CMPOP_TO_AST: dict[CmpOp, ast.cmpop] = {
    v: k() for k, v in _AST_CMPOP_TO_DOMAIN.items()
}


def cmpop_from_ast(op: ast.cmpop) -> CmpOp:
    return _AST_CMPOP_TO_DOMAIN[type(op)]


def cmpop_to_ast(op: CmpOp) -> ast.cmpop:
    return _DOMAIN_CMPOP_TO_AST[op]


_AST_CTX_TO_DOMAIN: dict[type[ast.expr_context], ExprContext] = {
    ast.Load: ExprContext.LOAD,
    ast.Store: ExprContext.STORE,
    ast.Del: ExprContext.DEL,
}
_DOMAIN_CTX_TO_AST: dict[ExprContext, ast.expr_context] = {
    v: k() for k, v in _AST_CTX_TO_DOMAIN.items()
}


def ctx_from_ast(ctx: ast.expr_context) -> ExprContext:
    return _AST_CTX_TO_DOMAIN[type(ctx)]


def ctx_to_ast(ctx: ExprContext | None) -> ast.expr_context:
    if ctx is None:
        return ast.Load()
    return _DOMAIN_CTX_TO_AST[ctx]
