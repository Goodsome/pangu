from code_dom.domain.value_objects.ast_stmt import AstStmtBase
from foundation.common_types.pascal_string import PascalString
from foundation.common_types.snake_string import SnakeString

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.domain.factories.ast_builder_helpers import (
    make_class,
    make_func,
    make_generic_base,
    parse_body,
    to_plural,
)
from code_generation.domain.factories.fqn_factory import FqnFactory
from code_generation.domain.factories.module_blueprint_builder import (
    ModuleBlueprintBuilder,
)


class InfrastructureBlueprintFactory:
    def create_infrastructure_modules(
        self, context: str, aggregate_name: str
    ) -> list[ModuleBlueprint]:
        return [
            self.create_orm_model(context, aggregate_name),
            self.create_orm_mapper(context, aggregate_name),
            self.create_sqlalchemy_repository(context, aggregate_name),
        ]

    def create_orm_model(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        plural = to_plural(aggregate_name)
        model_name = f"{pascal}Model"

        table_stmt = parse_body(f'__tablename__: str = "{plural}"')[0]
        id_stmt = parse_body("id: Mapped[UUID] = mapped_column(primary_key=True)")[0]

        model_cls = make_class(
            name=model_name,
            bases=[make_generic_base("BaseORM")],
            body=[table_stmt, id_stmt],
        )

        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_orm_model_fqn(context, aggregate_name)
            )
            .with_symbols(["BaseORM", "Mapped", "mapped_column", "UUID"])
            .with_stmt(model_cls)
            .build()
        )

    def create_orm_mapper(self, context: str, aggregate_name: str) -> ModuleBlueprint:
        snake = SnakeString(aggregate_name)
        pascal = PascalString(aggregate_name)
        id_name = f"{pascal}Id"
        model_name = f"{pascal}Model"

        m2e_func_name = f"{snake}_model_to_entity"
        m2e_code = f"return {pascal}(id={id_name}.reconstitute(model.id))"
        m2e_node = make_func(
            name=m2e_func_name,
            params=[("model", model_name)],
            returns=str(pascal),
            body=parse_body(m2e_code),
        )

        e2m_func_name = f"{snake}_entity_to_model"
        e2m_code = f"return {model_name}(id=entity.id.value)"
        e2m_node = make_func(
            name=e2m_func_name,
            params=[("entity", str(pascal))],
            returns=model_name,
            body=parse_body(e2m_code),
        )

        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_orm_mapper_fqn(context, aggregate_name)
            )
            .with_symbols([model_name, str(pascal), id_name])
            .with_stmt(m2e_node)
            .with_stmt(e2m_node)
            .build()
        )

    def create_sqlalchemy_repository(
        self, context: str, aggregate_name: str
    ) -> ModuleBlueprint:
        pascal = PascalString(aggregate_name)
        snake = SnakeString(aggregate_name)
        repo_interface_name = f"{pascal}Repository"
        repo_class_name = f"SqlAlchemy{pascal}Repository"
        id_name = f"{pascal}Id"
        model_name = f"{pascal}Model"

        m2e_func = f"{snake}_model_to_entity"
        e2m_func = f"{snake}_entity_to_model"

        session_field = parse_body("session: SqlAlchemySession")[0]

        add_code = f"""
model = {e2m_func}(aggregate)
self.session.add(model)
"""
        add_func = make_func(
            name="_add",
            params=[("self", None), ("aggregate", str(pascal))],
            returns="None",
            decorators=["override"],
            body=parse_body(add_code),
        )

        add_all_code = f"""
models = [{e2m_func}(a) for a in aggregates]
self.session.add_all(models)
"""
        add_all_func = make_func(
            name="_add_all",
            params=[("self", None), ("aggregates", f"list[{pascal}]")],
            returns="None",
            decorators=["override"],
            body=parse_body(add_all_code),
        )

        get_code = f"""
model = self.session.get({model_name}, id.value)
if not model:
    raise ValueError(f"{pascal} {{id}} not found")
return {m2e_func}(model)
"""
        get_func = make_func(
            name="_get",
            params=[("self", None), ("id", id_name)],
            returns=str(pascal),
            decorators=["override"],
            body=parse_body(get_code),
        )

        save_code = f"""
model = {e2m_func}(aggregate)
self.session.merge(model)
"""
        save_func = make_func(
            name="_save",
            params=[("self", None), ("aggregate", str(pascal))],
            returns="None",
            decorators=["override"],
            body=parse_body(save_code),
        )

        save_all_code = """
for aggregate in aggregates:
    self._save(aggregate)
"""
        save_all_func = make_func(
            name="_save_all",
            params=[("self", None), ("aggregates", f"list[{pascal}]")],
            returns="None",
            decorators=["override"],
            body=parse_body(save_all_code),
        )

        delete_code = f"""
model = self.session.get({model_name}, aggregate.id.value)
if model:
    self.session.delete(model)
"""
        delete_func = make_func(
            name="_delete",
            params=[("self", None), ("aggregate", str(pascal))],
            returns="None",
            decorators=["override"],
            body=parse_body(delete_code),
        )

        methods: list[AstStmtBase] = [
            session_field,
            add_func,
            add_all_func,
            get_func,
            save_func,
            save_all_func,
            delete_func,
        ]

        repo_cls = make_class(
            name=repo_class_name,
            bases=[make_generic_base(repo_interface_name)],
            decorators=["dataclass"],
            body=methods,
        )

        return (
            ModuleBlueprintBuilder(
                path=FqnFactory.create_sqlalchemy_repository_fqn(
                    context, aggregate_name
                )
            )
            .with_symbols(
                [
                    "dataclass",
                    "override",
                    "SqlAlchemySession",
                    repo_interface_name,
                    model_name,
                    str(pascal),
                    id_name,
                    m2e_func,
                    e2m_func,
                ]
            )
            .with_stmt(repo_cls)
            .build()
        )
