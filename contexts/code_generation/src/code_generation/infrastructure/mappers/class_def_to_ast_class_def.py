from code_dom.domain.value_objects.ast_stmt import AstClassDef
from code_generation.domain.value_objects.symbol_def import ClassDef


def class_def_to_ast_class_def(class_def: ClassDef) -> AstClassDef:
    return AstClassDef(
        name=class_def.name,
        bases=[],
        keywords=[],
        body=[],
    )