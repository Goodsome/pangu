import ast
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.infrastructure.mappers.ast_mapper_protocol import (
    AstMapperProtocol,
)
from codegen.code_metadata.infrastructure.mappers.ast_to_stmt import AstToStmt


class AstToBehaviorMixin:

    def function_def_to_behavior(
        self: AstMapperProtocol, node: ast.FunctionDef
    ) -> ParsedBehavior:
        description = ast.get_docstring(node)
        inputs = self.parse_node_to_attributes(node.args)
        if node.returns is None:
            output = ParsedType(origin="None")
        else:
            output = self.parse_node_to_type(node.returns)
        body = [AstToStmt.to_stmt(stmt) for stmt in node.body]
        return ParsedBehavior(
            name=node.name,
            description=description,
            inputs=inputs,
            output=output,
            body=body,
        )
