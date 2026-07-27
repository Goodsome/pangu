from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_stmt import AstAnnAssign, AstAssign
from code_generation.domain.value_objects.symbol_def import ParamDef


def param_to_ast_assign(param: ParamDef) -> AstAssign | AstAnnAssign:
    if param.type_annotation:
        return AstAnnAssign(
            target=AstName(id=param.name),
            annotation=AstName(id=param.type_annotation),
            value=None,
        )
    return AstAssign(
        targets=[AstName(id=param.name)],
        value=None,
    )
