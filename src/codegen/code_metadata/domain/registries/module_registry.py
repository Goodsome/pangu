from dataclasses import dataclass
from dataclasses import field
from typing import Callable
from codegen.code_metadata.domain.aggregates.module import DirectoryModule
from codegen.code_metadata.domain.aggregates.module import ExternalModule
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.code_metadata.domain.identifiers.module_id import ModuleId


@dataclass
class ModuleRegistry:
    init_modules: list[Module]
    on_module_registered: Callable[[Module], None] = lambda _: None
    _store_by_id: dict[ModuleId, Module] = field(init=False)
    _store_by_path: dict[str, Module] = field(init=False)

    def __post_init__(self):
        self._store_by_id = {}
        self._store_by_path = {}
        for module in self.init_modules:
            self._store_by_id[module.id] = module
            self._store_by_path[module.path] = module

    def find_by_id(self, module_id: ModuleId) -> Module | None:
        return self._store_by_id.get(module_id)

    def find_by_path(self, path: str) -> Module | None:
        return self._store_by_path.get(path)

    def register(self, module: Module) -> None:
        if module.id in self._store_by_id:
            return
        self._store_by_id[module.id] = module
        self._store_by_path[module.path] = module
        self.bind_parent_module(module)
        self.on_module_registered(module)

    def create_external_module(self, path: str) -> Module:
        module = ExternalModule(
            id=ModuleId.create(), name=path, path=path, components=[]
        )
        self.register(module)
        return module

    def create_directory_module(self, name: str, path: str) -> Module:
        module = DirectoryModule(
            id=ModuleId.create(),
            name=name,
            path=path,
            public_component_ids=[],
            sub_module_ids=[],
            dir_module_id=None,
        )
        self.register(module)
        return module

    def bind_parent_module(self, module: Module) -> None:
        if isinstance(module, ExternalModule):
            return
        splits = module.path.split(".")
        if len(splits) <= 2:
            return
        parent_path = ".".join(splits[:-1])
        parent_name = parent_path.split(".")[-2]
        parent_module = self.find_by_path(parent_path)
        if parent_module is None:
            parent_module = self.create_directory_module(
                name=parent_name, path=parent_path
            )
        assert isinstance(parent_module, DirectoryModule)
        parent_module.bind_sub_module_id(module.id)
        module.bind_dir_module_id(parent_module.id)
