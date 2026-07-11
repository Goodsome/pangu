from typing_extensions import assert_never
from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_arguments import AstArguments
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_assert import AstAssert
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_attribute import AstAttribute
from codegen.code_metadata.domain.value_objects.ast_await import AstAwait
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_aug_assign import AstAugAssign
from codegen.code_metadata.domain.value_objects.ast_bin_op import AstBinOp
from codegen.code_metadata.domain.value_objects.ast_bool_op import AstBoolOp
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_break import AstBreak
from codegen.code_metadata.domain.value_objects.ast_call import AstCall
from codegen.code_metadata.domain.value_objects.ast_compare import AstCompare
from codegen.code_metadata.domain.value_objects.ast_comprehension import (
    AstComprehension,
)
from codegen.code_metadata.domain.value_objects.ast_constant import AstConstant
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_continue import AstContinue
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_delete import AstDelete
from codegen.code_metadata.domain.value_objects.ast_dict import AstDict
from codegen.code_metadata.domain.value_objects.ast_dict_comp import AstDictComp
from codegen.code_metadata.domain.value_objects.ast_except_handler import (
    AstExceptHandler,
)
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_stmt import AstFor
from codegen.code_metadata.domain.value_objects.ast_formatted_value import (
    AstFormattedValue,
)
from codegen.code_metadata.domain.value_objects.ast_stmt import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_generator_exp import AstGeneratorExp
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_if_exp import AstIfExp
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_joined_str import AstJoinedStr
from codegen.code_metadata.domain.value_objects.ast_keyword import AstKeyword
from codegen.code_metadata.domain.value_objects.ast_lambda import AstLambda
from codegen.code_metadata.domain.value_objects.ast_list import AstList
from codegen.code_metadata.domain.value_objects.ast_list_comp import AstListComp
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_match import AstMatch
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_named_expr import AstNamedExpr
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_raise import AstRaise
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_return import AstReturn
from codegen.code_metadata.domain.value_objects.ast_set import AstSet
from codegen.code_metadata.domain.value_objects.ast_set_comp import AstSetComp
from codegen.code_metadata.domain.value_objects.ast_slice import AstSlice
from codegen.code_metadata.domain.value_objects.ast_starred import AstStarred
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_subscript import AstSubscript
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_try import AstTry
from codegen.code_metadata.domain.value_objects.ast_tuple import AstTuple
from codegen.code_metadata.domain.value_objects.ast_unary_op import AstUnaryOp
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_while import AstWhile
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_with import AstWith
from codegen.code_metadata.domain.value_objects.ast_yield import AstYield
from codegen.code_metadata.domain.value_objects.ast_yield_from import AstYieldFrom
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import (
    AstClassDef,
)


class AstVisitor:
    def visit(
        self,
        node: AstStmt
        | AstExpr
        | AstArguments
        | AstComprehension
        | AstKeyword
        | AstMatchCase
        | AstExceptHandler
        | Arg
        | list[AstStmt]
        | list[AstExpr]
        | list[AstKeyword]
        | None,
    ):
        if node is None:
            return
        match node:
            case AstReturn():
                self.visit_ast_return(node)
            case AstRaise():
                self.visit_ast_raise(node)
            case AstAssert():
                self.visit_ast_assert(node)
            case AstPass():
                self.visit_ast_pass(node)
            case AstBreak():
                self.visit_ast_break(node)
            case AstContinue():
                self.visit_ast_continue(node)
            case AstAssign():
                self.visit_ast_assign(node)
            case AstAnnAssign():
                self.visit_ast_ann_assign(node)
            case AstAugAssign():
                self.visit_ast_aug_assign(node)
            case AstExprStmt():
                self.visit_ast_expr_stmt(node)
            case AstDelete():
                self.visit_ast_delete(node)
            case AstFor():
                self.visit_ast_for(node)
            case AstWhile():
                self.visit_ast_while(node)
            case AstIf():
                self.visit_ast_if(node)
            case AstWith():
                self.visit_ast_with(node)
            case AstMatch():
                self.visit_ast_match(node)
            case AstTry():
                self.visit_ast_try(node)
            case AstFunctionDef():
                self.visit_ast_function_def(node)
            case AstImport():
                self.visit_ast_import(node)
            case AstImportFrom():
                self.visit_ast_import_from(node)
            case AstClassDef():
                self.visit_ast_class_def(node)
            case AstConstant():
                self.visit_ast_constant(node)
            case AstName():
                self.visit_ast_name(node)
            case AstAttribute():
                self.visit_ast_attribute(node)
            case AstCall():
                self.visit_ast_call(node)
            case AstBinOp():
                self.visit_ast_bin_op(node)
            case AstBoolOp():
                self.visit_ast_bool_op(node)
            case AstUnaryOp():
                self.visit_ast_unary_op(node)
            case AstCompare():
                self.visit_ast_compare(node)
            case AstIfExp():
                self.visit_ast_if_exp(node)
            case AstLambda():
                self.visit_ast_lambda(node)
            case AstJoinedStr():
                self.visit_ast_joined_str(node)
            case AstFormattedValue():
                self.visit_ast_formatted_value(node)
            case AstListComp():
                self.visit_ast_list_comp(node)
            case AstSetComp():
                self.visit_ast_set_comp(node)
            case AstDictComp():
                self.visit_ast_dict_comp(node)
            case AstGeneratorExp():
                self.visit_ast_generator_exp(node)
            case AstSlice():
                self.visit_ast_slice(node)
            case AstStarred():
                self.visit_ast_starred(node)
            case AstSubscript():
                self.visit_ast_subscript(node)
            case AstTuple():
                self.visit_ast_tuple(node)
            case AstList():
                self.visit_ast_list(node)
            case AstSet():
                self.visit_ast_set(node)
            case AstDict():
                self.visit_ast_dict(node)
            case AstYield():
                self.visit_ast_yield(node)
            case AstYieldFrom():
                self.visit_ast_yield_from(node)
            case AstAwait():
                self.visit_ast_await(node)
            case AstNamedExpr():
                self.visit_ast_named_expr(node)
            case AstKeyword():
                self.visit_ast_keyword(node)
            case AstArguments():
                self.visit_ast_arguments(node)
            case AstComprehension():
                self.visit_ast_comprehension(node)
            case AstMatchCase():
                self.visit_ast_match_case(node)
            case AstExceptHandler():
                self.visit_ast_except_handler(node)
            case Arg():
                self.visit_arg(node)
            case list():
                for item in node:
                    self.visit(item)
            case _:
                assert_never(node)

    def visit_ast_return(self, node: AstReturn):
        if node.value is not None:
            self.visit(node.value)

    def visit_ast_raise(self, node: AstRaise):
        if node.exc is not None:
            self.visit(node.exc)
        if node.cause is not None:
            self.visit(node.cause)

    def visit_ast_assert(self, node: AstAssert):
        self.visit(node.test)
        if node.msg is not None:
            self.visit(node.msg)

    def visit_ast_pass(self, node: AstPass):
        pass

    def visit_ast_break(self, node: AstBreak):
        pass

    def visit_ast_continue(self, node: AstContinue):
        pass

    def visit_ast_assign(self, node: AstAssign):
        self.visit(node.targets)
        if node.value is not None:
            self.visit(node.value)

    def visit_ast_ann_assign(self, node: AstAnnAssign):
        self.visit(node.target)
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)

    def visit_ast_aug_assign(self, node: AstAugAssign):
        self.visit(node.target)
        self.visit(node.value)

    def visit_ast_expr_stmt(self, node: AstExprStmt):
        self.visit(node.value)

    def visit_ast_delete(self, node: AstDelete):
        for target in node.targets:
            self.visit(target)

    def visit_ast_for(self, node: AstFor):
        self.visit(node.target)
        self.visit(node.iter)
        self.visit(node.body)
        self.visit(node.orelse)

    def visit_ast_while(self, node: AstWhile):
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)

    def visit_ast_if(self, node: AstIf):
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)

    def visit_ast_with(self, node: AstWith):
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is not None:
                self.visit(item.optional_vars)
        self.visit(node.body)

    def visit_ast_match(self, node: AstMatch):
        self.visit(node.subject)
        for case in node.cases:
            self.visit(case)

    def visit_ast_try(self, node: AstTry):
        self.visit(node.body)
        for handler in node.handlers:
            self.visit(handler)
        self.visit(node.orelse)
        self.visit(node.finalbody)

    def visit_ast_function_def(self, node: AstFunctionDef):
        self.visit(node.decorator_list)
        for arg in node.arguments:
            self.visit(arg)
        self.visit(node.body)
        if node.returns is not None:
            self.visit(node.returns)

    def visit_ast_import(self, node: AstImport):
        pass

    def visit_ast_import_from(self, node: AstImportFrom):
        pass

    def visit_ast_class_def(self, node: AstClassDef):
        self.visit(node.bases)
        self.visit(node.body)
        self.visit(node.decorator_list)

    def visit_ast_constant(self, node: AstConstant):
        pass

    def visit_ast_name(self, node: AstName):
        pass

    def visit_ast_attribute(self, node: AstAttribute):
        self.visit(node.value)

    def visit_ast_call(self, node: AstCall):
        self.visit(node.func)
        self.visit(node.args)
        self.visit(node.kwargs)

    def visit_ast_bin_op(self, node: AstBinOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_ast_bool_op(self, node: AstBoolOp):
        self.visit(node.values)

    def visit_ast_unary_op(self, node: AstUnaryOp):
        self.visit(node.operand)

    def visit_ast_compare(self, node: AstCompare):
        self.visit(node.left)
        self.visit(node.comparators)

    def visit_ast_if_exp(self, node: AstIfExp):
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)

    def visit_ast_lambda(self, node: AstLambda):
        for arg in node.args.posonlyargs:
            self.visit(arg)
        for arg in node.args.args:
            self.visit(arg)
        if node.args.vararg is not None:
            self.visit(node.args.vararg)
        for arg in node.args.kwonlyargs:
            self.visit(arg)
        if node.args.kwarg is not None:
            self.visit(node.args.kwarg)
        self.visit(node.body)

    def visit_ast_joined_str(self, node: AstJoinedStr):
        self.visit(node.values)

    def visit_ast_formatted_value(self, node: AstFormattedValue):
        self.visit(node.value)
        if node.format_spec is not None:
            self.visit(node.format_spec)

    def visit_ast_list_comp(self, node: AstListComp):
        self.visit(node.elt)
        for gen in node.generators:
            self.visit(gen)

    def visit_ast_set_comp(self, node: AstSetComp):
        self.visit(node.elt)
        for gen in node.generators:
            self.visit(gen)

    def visit_ast_dict_comp(self, node: AstDictComp):
        self.visit(node.key)
        self.visit(node.value)
        for gen in node.generators:
            self.visit(gen)

    def visit_ast_generator_exp(self, node: AstGeneratorExp):
        self.visit(node.elt)
        for gen in node.generators:
            self.visit(gen)

    def visit_ast_slice(self, node: AstSlice):
        if node.lower is not None:
            self.visit(node.lower)
        if node.upper is not None:
            self.visit(node.upper)
        if node.step is not None:
            self.visit(node.step)

    def visit_ast_starred(self, node: AstStarred):
        self.visit(node.value)

    def visit_ast_subscript(self, node: AstSubscript):
        self.visit(node.value)
        self.visit(node.slice)

    def visit_ast_tuple(self, node: AstTuple):
        self.visit(node.elts)

    def visit_ast_list(self, node: AstList):
        self.visit(node.elts)

    def visit_ast_set(self, node: AstSet):
        self.visit(node.elts)

    def visit_ast_dict(self, node: AstDict):
        for key in node.keys:
            if key is not None:
                self.visit(key)
        self.visit(node.values)

    def visit_ast_yield(self, node: AstYield):
        if node.value is not None:
            self.visit(node.value)

    def visit_ast_yield_from(self, node: AstYieldFrom):
        self.visit(node.value)

    def visit_ast_await(self, node: AstAwait):
        self.visit(node.value)

    def visit_ast_named_expr(self, node: AstNamedExpr):
        self.visit(node.target)
        self.visit(node.value)

    def visit_ast_keyword(self, node: AstKeyword):
        self.visit(node.value)

    def visit_arg(self, node: Arg):
        if node.annotation is not None:
            self.visit(node.annotation)

    def visit_ast_arguments(self, node: AstArguments):
        for arg in node.posonlyargs:
            self.visit(arg)
        for arg in node.args:
            self.visit(arg)
        if node.vararg is not None:
            self.visit(node.vararg)
        for arg in node.kwonlyargs:
            self.visit(arg)
        for default in node.kw_defaults:
            if default is not None:
                self.visit(default)
        if node.kwarg is not None:
            self.visit(node.kwarg)
        self.visit(node.defaults)

    def visit_ast_comprehension(self, node: AstComprehension):
        self.visit(node.target)
        self.visit(node.iter)
        self.visit(node.ifs)

    def visit_ast_match_case(self, node: AstMatchCase):
        if node.guard is not None:
            self.visit(node.guard)
        self.visit(node.body)

    def visit_ast_except_handler(self, node: AstExceptHandler):
        if node.type is not None:
            self.visit(node.type)
        self.visit(node.body)
