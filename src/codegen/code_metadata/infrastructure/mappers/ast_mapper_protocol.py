import ast
from typing import Protocol
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_type import ParsedType


class AstMapperProtocol(Protocol):

    def parse_node_to_behavior(self, node: ast.AST) -> ParsedBehavior: ...

    def parse_node_to_attribute(self, node: ast.AST) -> ParsedAttribute: ...

    def parse_node_to_type(self, node: ast.AST) -> ParsedType: ...

    def parse_node_to_attributes(
        self, node: ast.arguments
    ) -> list[ParsedAttribute]: ...
