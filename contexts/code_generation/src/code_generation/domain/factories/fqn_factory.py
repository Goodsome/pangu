from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.snake_string import SnakeString


class FqnFactory:
    @staticmethod
    def create_aggregate_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.domain.aggregates.{SnakeString(aggregate_name)}")

    @staticmethod
    def create_identity_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.domain.identities.{SnakeString(aggregate_name)}_id"
        )

    @staticmethod
    def create_repository_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.domain.repositories.{SnakeString(aggregate_name)}_repository"
        )

    @staticmethod
    def create_repo_provider_fqn(context: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.application.ports.repo_provider")

    @staticmethod
    def create_unit_of_work_fqn(context: str) -> ModuleFqn:
        return FqnFactory.create_repo_provider_fqn(context)

    @staticmethod
    def create_sql_alchemy_unit_of_work_fqn(context: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.infrastructure.persistence.repositories.sql_alchemy_unit_of_work"
        )

    @staticmethod
    def create_dto_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.application.dtos.{SnakeString(aggregate_name)}_dto"
        )

    @staticmethod
    def create_dto_to_entity_mapper_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        snake_name = SnakeString(aggregate_name)
        return ModuleFqn(
            f"{context}.application.mappers.{snake_name}_dto_to_{snake_name}"
        )

    @staticmethod
    def create_update_entity_from_dto_mapper_fqn(
        context: str, aggregate_name: str
    ) -> ModuleFqn:
        snake_name = SnakeString(aggregate_name)
        return ModuleFqn(f"{context}.application.mappers.update_{snake_name}_from_dto")

    @staticmethod
    def create_entity_to_dto_mapper_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        snake_name = SnakeString(aggregate_name)
        return ModuleFqn(
            f"{context}.application.mappers.{snake_name}_to_{snake_name}_dto"
        )

    @staticmethod
    def create_create_command_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.application.commands.create_{SnakeString(aggregate_name)}"
        )

    @staticmethod
    def create_update_command_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.application.commands.update_{SnakeString(aggregate_name)}"
        )

    @staticmethod
    def create_delete_command_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        return ModuleFqn(
            f"{context}.application.commands.delete_{SnakeString(aggregate_name)}"
        )

    @staticmethod
    def create_orm_model_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        snake_name = SnakeString(aggregate_name)
        return ModuleFqn(
            f"{context}.infrastructure.persistence.models.{snake_name}_model"
        )

    @staticmethod
    def create_orm_mapper_fqn(context: str, aggregate_name: str) -> ModuleFqn:
        snake_name = SnakeString(aggregate_name)
        return ModuleFqn(
            f"{context}.infrastructure.persistence.mappers.{snake_name}_mapper"
        )

    @staticmethod
    def create_sqlalchemy_repository_fqn(
        context: str, aggregate_name: str
    ) -> ModuleFqn:
        snake_name = SnakeString(aggregate_name)
        return ModuleFqn(
            f"{context}.infrastructure.persistence.repositories.sql_alchemy_{snake_name}_repository"
        )
