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