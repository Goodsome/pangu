from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.snake_string import SnakeString


class FqnFactory:

    @staticmethod
    def create_aggregate_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.domain.aggregates.{SnakeString(name)}")

    @staticmethod
    def create_identity_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.domain.identities.{SnakeString(name)}")

    @staticmethod
    def create_repository_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.domain.repositories.{SnakeString(name)}")

    @staticmethod
    def create_unit_of_work_fqn(context: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.application.ports.unit_of_work")

    @staticmethod
    def create_dto_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.application.dtos.{SnakeString(name)}_dto")

    @staticmethod
    def create_dto_to_entity_mapper_fqn(context: str, name: str) -> ModuleFqn:
        snake_name = SnakeString(name)
        return ModuleFqn(f"{context}.application.mappers.{snake_name}_dto_to_{snake_name}")

    @staticmethod
    def create_entity_to_dto_mapper_fqn(context: str, name: str) -> ModuleFqn:
        snake_name = SnakeString(name)
        return ModuleFqn(f"{context}.application.mappers.{snake_name}_to_{snake_name}_dto")

    @staticmethod
    def create_create_command_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.application.commands.create_{SnakeString(name)}")

    @staticmethod
    def create_update_command_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.application.commands.update_{SnakeString(name)}")

    @staticmethod
    def create_delete_command_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.application.commands.delete_{SnakeString(name)}")