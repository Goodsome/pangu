import ast
from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.infrastructure.mappers.ast_mapper_protocol import (
    AstMapperProtocol,
)


class AstClassToComponent:

    def class_def_to_component(
        self: AstMapperProtocol, node: ast.ClassDef, imports: list[ImportDto]
    ) -> ParsedComponent:
        bases = [self.parse_node_to_type(b) for b in node.bases]
        attributes: list[ParsedAttribute] = []
        behaviors: list[ParsedBehavior] = []
        for item in node.body:
            if isinstance(item, (ast.AnnAssign, ast.Assign)):
                pa = self.parse_node_to_attribute(item)
                attributes.append(pa)
            elif isinstance(item, ast.FunctionDef):
                b = self.parse_node_to_behavior(item)
                behaviors.append(b)
        return ParsedComponent(
            name=node.name,
            description=ast.get_docstring(node) or "",
            bases=bases,
            attributes=attributes,
            behaviors=behaviors,
            imports=imports,
            members=[],
            discriminator=None,
        )
