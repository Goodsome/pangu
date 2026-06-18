from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID
from uuid import uuid4
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import ColumnElement
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.infrastructure.orm_models.base import BaseORM

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


class CodeNodeModel(BaseORM):
    """统一节点表"""

    __tablename__: str = "code_nodes"
    __mapper_args__: dict[str, str] = {"polymorphic_on": "kind"}
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    fqn: Mapped[Fqn] = mapped_column(String(1024), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    properties: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    last_sync_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    outbound_edges: Mapped[list[CodeEdgeModel]] = relationship(
        "CodeEdgeModel",
        foreign_keys="[CodeEdgeModel.source_id]",
        back_populates="source_entity",
        cascade="all, delete-orphan",
        order_by="CodeEdgeModel.position.asc()",
    )
    inbound_edges: Mapped[list[CodeEdgeModel]] = relationship(
        "CodeEdgeModel",
        foreign_keys="[CodeEdgeModel.target_id]",
        back_populates="target_entity",
        viewonly=True,
    )


class ModuleNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.MODULE}

    @hybrid_property
    def is_package(self) -> bool:
        return self.properties.get("is_package", False)

    @is_package.setter
    def _is_package_setter(self, value: bool) -> None:
        self.properties = {**self.properties, "is_package": value}

    @is_package.expression
    @classmethod
    def _is_package_expression(cls) -> ColumnElement[bool]:
        return cls.properties["is_package"].as_boolean()

    @hybrid_property
    def exprs(self) -> list[dict[str, object]]:
        return self.properties.get("exprs", [])

    @exprs.setter
    def _exprs_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "exprs": value}


class ClassNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.CLASS}

    @hybrid_property
    def decorator_list(self) -> list[dict[str, object]]:
        return self.properties.get("decorator_list", [])

    @decorator_list.setter
    def _decorator_lista_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "decorator_list": value}

    @hybrid_property
    def bases(self) -> list[dict[str, object]]:
        return self.properties.get("bases", [])

    @bases.setter
    def _bases_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "bases": value}

    @hybrid_property
    def type_params(self) -> list[dict[str, object]]:
        return self.properties.get("type_params", [])

    @type_params.setter
    def _type_params_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "type_params": value}


class FunctionNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.FUNCTION}

    @hybrid_property
    def is_async(self) -> bool:
        return self.properties.get("is_async", False)

    @is_async.setter
    def _is_async_setter(self, value: bool) -> None:
        self.properties = {**self.properties, "is_async": value}

    @hybrid_property
    def decorator_list(self) -> list[dict[str, object]]:
        return self.properties.get("decorator_list", [])

    @decorator_list.setter
    def _decorator_list_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "decorator_list": value}

    @hybrid_property
    def returns(self) -> dict[str, Any] | None:
        return self.properties.get("returns")

    @returns.setter
    def _returns_setter(self, value: dict[str, Any] | None) -> None:
        if value is None:
            return
        self.properties = {**self.properties, "returns": value}

    @hybrid_property
    def body(self) -> list[dict[str, object]]:
        return self.properties.get("body", [])

    @body.setter
    def _body_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "body": value}


class MethodNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.METHOD}

    @hybrid_property
    def is_async(self) -> bool:
        return self.properties.get("is_async", False)

    @is_async.setter
    def _is_async_setter(self, value: bool) -> None:
        self.properties = {**self.properties, "is_async": value}

    @hybrid_property
    def decorator_list(self) -> list[dict[str, object]]:
        return self.properties.get("decorator_list", [])

    @decorator_list.setter
    def _decorator_list_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "decorator_list": value}

    @hybrid_property
    def returns(self) -> dict[str, Any] | None:
        return self.properties.get("returns")

    @returns.setter
    def _returns_setter(self, value: dict[str, Any] | None) -> None:
        if value is None:
            return
        self.properties = {**self.properties, "returns": value}

    @hybrid_property
    def body(self) -> list[dict[str, object]]:
        return self.properties.get("body", [])

    @body.setter
    def _body_setter(self, value: list[dict[str, object]]):
        self.properties = {**self.properties, "body": value}

    @hybrid_property
    def check_reachable(self) -> bool:
        return self.properties.get("check_reachable", True)

    @check_reachable.expression
    def check_reachable(cls) -> ColumnElement[bool]:
        return cls.properties["check_reachable"].as_boolean()

    @check_reachable.setter
    def _check_reachable_setter(self, value: bool) -> None:
        self.properties = {**self.properties, "check_reachable": value}


class VariableNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.VARIABLE}

    @hybrid_property
    def value(self) -> dict[str, Any] | None:
        return self.properties.get("value")

    @value.setter
    def _value_setter(self, value: dict[str, Any] | None) -> None:
        if value is None:
            return
        self.properties = {**self.properties, "value": value}

    @hybrid_property
    def annotation(self) -> dict[str, Any] | None:
        return self.properties.get("annotation")

    @annotation.setter
    def _annotation_setter(self, value: dict[str, Any] | None) -> None:
        if value is None:
            return
        self.properties = {**self.properties, "annotation": value}


class ParameterNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.PARAMETER}

    @hybrid_property
    def value(self) -> dict[str, Any] | None:
        return self.properties.get("value")

    @value.setter
    def _value_setter(self, value: dict[str, Any] | None) -> None:
        if value is None:
            return
        self.properties = {**self.properties, "value": value}

    @hybrid_property
    def annotation(self) -> dict[str, Any] | None:
        return self.properties.get("annotation")

    @annotation.setter
    def _annotation_setter(self, value: dict[str, Any] | None) -> None:
        if value is None:
            return
        self.properties = {**self.properties, "annotation": value}


class ExternalNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.EXTERNAL}


class ClassTypeNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.CLASS_TYPE}


class UnionTypeNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.UNION_TYPE}


class GenericTypeNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.GENERIC_TYPE}


class TypeVarNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.TYPE_VAR}
