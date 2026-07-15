from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.snake_string import SnakeString


class FqnFactory:

    @staticmethod
    def create_aggregate_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.domain.aggregates.{SnakeString(name)}")

    @staticmethod
    def create_identity_fqn(context: str, name: str) -> ModuleFqn:
        return ModuleFqn(f"{context}.domain.identities.{SnakeString(name)}")