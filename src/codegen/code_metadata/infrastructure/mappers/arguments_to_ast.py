import ast
from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.ast_arguments import AstArguments
from codegen.code_metadata.infrastructure.mappers.expr_to_ast import ExprToAst


class ArgumentsToAst:

    @staticmethod
    def to_node(args: AstArguments) -> ast.arguments:
        return ast.arguments(
            posonlyargs=[ArgumentsToAst._to_arg(a) for a in args.posonlyargs],
            args=[ArgumentsToAst._to_arg(a) for a in args.args],
            vararg=ArgumentsToAst._to_arg(args.vararg) if args.vararg else None,
            kwonlyargs=[ArgumentsToAst._to_arg(a) for a in args.kwonlyargs],
            kw_defaults=[
                ExprToAst.to_node(d) if d is not None else None
                for d in args.kw_defaults
            ],
            kwarg=ArgumentsToAst._to_arg(args.kwarg) if args.kwarg else None,
            defaults=[ExprToAst.to_node(d) for d in args.defaults],
        )

    @staticmethod
    def _to_arg(arg: Arg) -> ast.arg:
        annotation = ExprToAst.to_node(arg.annotation)
        return ast.arg(arg=arg.arg, annotation=annotation)
