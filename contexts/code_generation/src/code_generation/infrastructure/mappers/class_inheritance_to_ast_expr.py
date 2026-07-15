from code_dom.domain.value_objects.ast_expr import AstExprBase, AstList, AstSubscript, AstTuple
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_generation.domain.value_objects.symbol_def import ClassInheritance


def class_inheritance_to_ast_expr(inheritance: ClassInheritance) -> AstExprBase:
    if not inheritance.args:
        return AstName(id=inheritance.name)
    args: list[AstExprBase] = [AstName(id=arg) for arg in inheritance.args]
    if len(args) == 1:
        slice = args[0]
    else:
        slice = AstTuple(elts=args)
    return AstSubscript(
        value=AstName(id=inheritance.name),
        slice=slice
    )