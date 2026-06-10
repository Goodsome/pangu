import ast
from dataclasses import dataclass
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class AstNodeToParsedType:

    def _node_to_type(self, node: ast.AST) -> ParsedType:
        if isinstance(node, ast.Expr):
            return self.expr_to_type(node)
        elif isinstance(node, ast.Name):
            return self.name_to_type(node)
        elif isinstance(node, ast.Subscript):
            return self.subscript_to_type(node)
        elif isinstance(node, ast.BinOp):
            return self.binop_to_type(node)
        elif isinstance(node, ast.Constant):
            return self.constant_to_type(node)
        elif isinstance(node, ast.Attribute):
            return self.attribute_to_type(node)
        elif isinstance(node, ast.List):
            return self.list_to_type(node)
        raise NotImplementedError(
            f"Unsupported AST node: {node}, {ast.dump(node)}, {ast.unparse(node)}"
        )

    def expr_to_type(self, expr: ast.Expr) -> ParsedType:
        return self._node_to_type(expr.value)

    def subscript_to_type(self, expr: ast.Subscript) -> ParsedType:
        container = self._node_to_type(expr.value)
        args: tuple[ParsedType, ...]
        if isinstance(expr.slice, ast.Tuple):
            args = tuple((self._node_to_type(slice) for slice in expr.slice.elts))
        else:
            args = (self._node_to_type(expr.slice),)
        container.args = args
        return container

    def name_to_type(self, expr: ast.Name) -> ParsedType:
        name = expr.id
        return ParsedType(origin=name)

    def binop_to_type(self, expr: ast.BinOp) -> ParsedType:
        match expr.op:
            case ast.BitOr():
                left_type = self._node_to_type(expr.left)
                right_type = self._node_to_type(expr.right)
                return ParsedType(
                    origin=PythonBuiltinType.UNION, args=(left_type, right_type)
                )
            case _:
                raise NotImplementedError(
                    f"不支持的类型注解二元操作符: {type(expr.op).__name__} (节点: {ast.dump(expr)})"
                )

    def constant_to_type(self, expr: ast.Constant) -> ParsedType:
        """
        处理常量节点。在类型注解中，主要用于处理省略号 (...) 和 前向引用 (字符串)。
        """
        match expr.value:
            case val if val is ...:
                return ParsedType(origin=PythonBuiltinType.ELLIPSIS)
            case str(forward_ref_name):
                return ParsedType(origin=forward_ref_name)
            case None:
                return ParsedType(origin=PythonBuiltinType.NONE)
            case _:
                raise NotImplementedError(
                    f"不支持的类型注解常量值: {expr.value} (节点: {ast.dump(expr)})"
                )

    def attribute_to_type(self, expr: ast.Attribute) -> ParsedType:
        origin = ast.unparse(expr)
        return ParsedType(origin=origin)

    def list_to_type(self, expr: ast.List) -> ParsedType:
        args = tuple((self._node_to_type(s) for s in expr.elts))
        return ParsedType(origin=PythonBuiltinType.LIST, args=args)
