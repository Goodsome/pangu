from dataclasses import dataclass
from dataclasses import field
from codegen.code_metadata.domain.enums.component_type import ComponentType
from codegen.code_metadata.domain.enums.component_dir import ComponentDir
from codegen.code_metadata.domain.policies.aggregate_policy import AggregatePolicy
from codegen.code_metadata.domain.policies.context_policy import ContextPolicy
from codegen.code_metadata.domain.policies.core_policy import CorePolicy
from codegen.code_metadata.domain.policies.entity_policy import EntityPolicy
from codegen.code_metadata.domain.policies.enum_policy import EnumPolicy
from codegen.code_metadata.domain.policies.event_policy import EventPolicy
from codegen.code_metadata.domain.policies.exception_policy import ExceptionPolicy
from codegen.code_metadata.domain.policies.external_policy import ExternalPolicy
from codegen.code_metadata.domain.policies.factory_policy import FactoryPolicy
from codegen.code_metadata.domain.policies.identifier_policy import IdentifierPolicy
from codegen.code_metadata.domain.policies.mapper_policy import MapperPolicy
from codegen.code_metadata.domain.policies.registry_policy import RegistryPolicy
from codegen.code_metadata.domain.policies.repository_policy import RepositoryPolicy
from codegen.code_metadata.domain.policies.policy_policy import PolicyPolicy
from codegen.code_metadata.domain.policies.orm_model_policy import OrmModelPolicy
from codegen.code_metadata.domain.policies.gateway_policy import GatewayPolicy
from codegen.code_metadata.domain.policies.service_policy import ServicePolicy
from codegen.code_metadata.domain.policies.value_object_policy import ValueObjectPolicy
from codegen.code_metadata.domain.policies.adapter_policy import AdapterPolicy
from codegen.code_metadata.domain.policies.cli_policy import CliPolicy
from codegen.code_metadata.domain.policies.command_policy import CommandPolicy
from codegen.code_metadata.domain.policies.component_policy import ComponentPolicy
from codegen.code_metadata.domain.policies.database_policy import DatabasePolicy
from codegen.code_metadata.domain.policies.dto_policy import DtoPolicy
from codegen.code_metadata.domain.policies.port_policy import PortPolicy
from codegen.code_metadata.domain.policies.query_policy import QueryPolicy


@dataclass
class ComponentPolicyFactory:
    _policies: list[ComponentPolicy] = field(init=False)
    _registry: dict[ComponentType, ComponentPolicy] = field(init=False)

    def __post_init__(self):
        self._policies = [
            AggregatePolicy(),
            CorePolicy(),
            DtoPolicy(),
            EntityPolicy(),
            EnumPolicy(),
            ExternalPolicy(),
            ValueObjectPolicy(),
            IdentifierPolicy(),
            QueryPolicy(),
            CommandPolicy(),
            PortPolicy(),
            ServicePolicy(),
            MapperPolicy(),
            FactoryPolicy(),
            EventPolicy(),
            ExceptionPolicy(),
            RepositoryPolicy(),
            PolicyPolicy(),
            OrmModelPolicy(),
            GatewayPolicy(),
            ContextPolicy(),
            RegistryPolicy(),
            AdapterPolicy(),
            DatabasePolicy(),
            CliPolicy(),
        ]
        self._registry = {p.component_type: p for p in self._policies}

    def get_policy(self, component_type: ComponentType) -> ComponentPolicy:
        cp = self._registry.get(component_type)
        if cp is None:
            raise ValueError(f"Unknown component type: {component_type}")
        return cp

    def get_policies(self) -> list[ComponentPolicy]:
        return self._policies

    def get_dir_to_type_registry(self) -> dict[ComponentDir, ComponentType]:
        return {
            p.dir_name: p.component_type
            for p in self._policies
            if p.component_type is not ComponentType.EXTERNAL
        }
