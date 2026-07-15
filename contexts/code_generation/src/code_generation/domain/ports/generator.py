from abc import ABC, abstractmethod

from code_generation.domain.entities.module_blueprint import ModuleBlueprint


class Generator(ABC):

    @abstractmethod
    def write_modules(self, modules: list[ModuleBlueprint]) -> None:
        ...
        