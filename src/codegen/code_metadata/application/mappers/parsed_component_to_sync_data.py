from dataclasses import dataclass
from typing import overload
from codegen.code_metadata.application.dtos.call_expr_dto import CallExprDto
from codegen.code_metadata.application.dtos.dict_expr_dto import DictExprDto
from codegen.code_metadata.application.dtos.dict_item_dto import DictItemDto
from codegen.code_metadata.application.dtos.lambda_expr_dto import LambdaExprDto
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.application.dtos.reference_expr_dto import ReferenceExprDto
from codegen.code_metadata.application.dtos.sequence_expr_dto import SequenceExprDto
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)
from codegen.code_metadata.domain.value_objects.behavior_sync_data import (
    BehaviorSyncData,
)
from codegen.code_metadata.domain.value_objects.call_expr import CallExpr
from codegen.code_metadata.domain.value_objects.component_sync_data import (
    ComponentSyncData,
)
from codegen.code_metadata.domain.value_objects.dict_expr import DictExpr
from codegen.code_metadata.domain.value_objects.dict_item import DictItem
from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.lambda_expr import LambdaExpr
from codegen.code_metadata.domain.value_objects.reference_expr import ReferenceExpr
from codegen.code_metadata.domain.value_objects.sequence_expr import SequenceExpr
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


@dataclass
class ParsedComponentToSyncData:
    resolver: ReferenceResolver

    def map(
        self,
        context: str,
        parsed_component: ParsedComponent,
        component_type: ComponentType,
        layer: ArchitectureLayer,
    ) -> ComponentSyncData:
        bases = [self.parsed_to_type(base) for base in parsed_component.bases]
        attributes = [
            self.to_attribute_sync_data(attr) for attr in parsed_component.attributes
        ]
        behaviors = [self.to_behavior(b) for b in parsed_component.behaviors]
        members = self.translate_members(parsed_component.members)
        discriminator = parsed_component.discriminator
        return ComponentSyncData(
            context=context,
            name=parsed_component.name,
            type=component_type,
            description=parsed_component.description,
            layer=layer,
            bases=bases,
            attributes=attributes,
            behaviors=behaviors,
            members=members,
            discriminator=discriminator,
        )

    @overload
    def parsed_to_type(self, parsed_type: None) -> None: ...

    @overload
    def parsed_to_type(self, parsed_type: ParsedType) -> TypeDef: ...

    def parsed_to_type(self, parsed_type: ParsedType | None) -> TypeDef | None:
        if parsed_type is None:
            return None
        origin = self.resolver.resolve_target(parsed_type.origin)
        args = tuple((self.parsed_to_type(arg) for arg in parsed_type.args))
        return TypeDef(origin=origin, args=args)

    def parsed_to_expr(self, expr: ParsedExpr | None) -> ExprDef | None:
        if expr is None:
            return None
        return self._map_expr(expr)

    def _map_expr(self, expr: ParsedExpr) -> ExprDef:
        match expr.kind:
            case ExprKind.CONSTANT:
                return expr
            case ExprKind.REFERENCE:
                return self._map_reference(expr)
            case ExprKind.CALL:
                return self._map_call(expr)
            case ExprKind.SEQUENCE:
                return self._map_sequence(expr)
            case ExprKind.DICT:
                return self._map_dict(expr)
            case ExprKind.LAMBDA:
                return self._map_lambda(expr)
            case _:
                raise ValueError(f"Unsupported expr kind: {expr.kind}")

    def _map_reference(self, expr: ReferenceExprDto) -> ReferenceExpr:
        source = self.parsed_to_expr(expr.source)
        source_target = None
        if source and source.kind == ExprKind.REFERENCE:
            source_target = source.target
        target = self.resolver.resolve_target(expr.target, source_target)
        return ReferenceExpr(target=target, source=source)

    def _map_call(self, expr: CallExprDto) -> CallExpr:
        callee = self._map_expr(expr.callee)
        args = [self._map_expr(arg) for arg in expr.args]
        kwargs = {k: self._map_expr(v) for k, v in expr.kwargs.items()}
        return CallExpr(callee=callee, args=args, kwargs=kwargs)

    def _map_sequence(self, expr: SequenceExprDto) -> SequenceExpr:
        container_type = expr.container_type
        elements = [self._map_expr(elem) for elem in expr.elements]
        return SequenceExpr(container_type=container_type, elements=elements)

    def _map_dict(self, expr: DictExprDto) -> DictExpr:
        items = [self._map_dict_item(item) for item in expr.items]
        return DictExpr(items=items)

    def _map_dict_item(self, item: DictItemDto) -> DictItem:
        key = self._map_expr(item.key) if item.key else None
        value = self._map_expr(item.value)
        return DictItem(key=key, value=value)

    def _map_lambda(self, expr: LambdaExprDto) -> LambdaExpr:
        body = self._map_expr(expr.body)
        return LambdaExpr(params=expr.params, body=body)

    def to_attribute_sync_data(
        self, parsed_attribute: ParsedAttribute
    ) -> AttributeSyncData:
        type_def = self.parsed_to_type(parsed_attribute.type)
        expr_def = self.parsed_to_expr(parsed_attribute.value)
        return AttributeSyncData(
            name=parsed_attribute.name, type=type_def, value=expr_def
        )

    def to_behavior(self, parsed_behavior: ParsedBehavior) -> BehaviorSyncData:
        inputs = [self.to_attribute_sync_data(a) for a in parsed_behavior.inputs]
        output = self.parsed_to_type(parsed_behavior.output)
        return BehaviorSyncData(
            name=parsed_behavior.name,
            description=parsed_behavior.description or "",
            inputs=inputs,
            output=output,
            body=parsed_behavior.body,
        )

    def translate_members(self, parsed_members: list[str]) -> list[ComponentId]:
        return [self.resolver.get_component_id(name) for name in parsed_members]
