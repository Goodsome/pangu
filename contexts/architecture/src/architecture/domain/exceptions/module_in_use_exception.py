from foundation.common_types.fqns.fqn import ModuleFqn


class ModuleInUseException(Exception):
    def __init__(self, module_fqn: ModuleFqn, callers: list[ModuleFqn]):
        self.module_fqn: ModuleFqn = module_fqn
        self.callers: list[ModuleFqn] = callers
        super().__init__(f"Module {module_fqn} is in use by {', '.join(callers)}")
