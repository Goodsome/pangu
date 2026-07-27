from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_stmt import AstClassDef
from code_generation.domain.value_objects.symbol_def import ClassDef
from code_generation.infrastructure.mappers.class_inheritance_to_ast_expr import (
    class_inheritance_to_ast_expr,
)
from code_generation.infrastructure.mappers.method_def_to_ast_function_def import (
    method_def_to_ast_function_def,
)


def class_def_to_ast_class_def(class_def: ClassDef) -> AstClassDef:
    bases = [class_inheritance_to_ast_expr(base) for base in class_def.inherits]
    body = [method_def_to_ast_function_def(m) for m in class_def.methods]
    decorator_list = [AstName(id=d) for d in class_def.decorators]
    return AstClassDef(
        name=class_def.name,
        bases=bases,
        keywords=[],
        body=body,
        decorator_list=decorator_list,
    )