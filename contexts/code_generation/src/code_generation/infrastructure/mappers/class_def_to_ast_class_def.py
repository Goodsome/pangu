from code_dom.domain.value_objects.ast_expr import AstExprBase
from code_dom.domain.value_objects.ast_stmt import AstClassDef
from code_generation.domain.value_objects.symbol_def import ClassDef
from code_generation.infrastructure.mappers.class_inheritance_to_ast_expr import class_inheritance_to_ast_expr


def class_def_to_ast_class_def(class_def: ClassDef) -> AstClassDef:
    bases = [class_inheritance_to_ast_expr(base) for base in class_def.inherits]
    return AstClassDef(
        name=class_def.name,
        bases=bases,
        keywords=[],
        body=[],
    )