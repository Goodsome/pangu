from enum import StrEnum
from enum import auto


class ComponentDir(StrEnum):
    CORE = auto()
    AGGREGATES = auto()
    ENTITIES = auto()
    VALUE_OBJECTS = auto()
    ENUMS = auto()
    SERVICES = auto()
    EXCEPTIONS = auto()
    REPOSITORIES = auto()
    IDENTIFIERS = auto()
    DTOS = auto()
    QUERIES = auto()
    COMMANDS = auto()
    MAPPERS = auto()
    PORTS = auto()
    ORM_MODELS = auto()
    GATEWAYS = auto()
    POLICIES = auto()
    FACTORIES = auto()
    EVENTS = auto()
    CLI = auto()
    CONTEXTS = auto()
    REGISTRIES = auto()
    DATABASE = auto()
    ADAPTERS = auto()
