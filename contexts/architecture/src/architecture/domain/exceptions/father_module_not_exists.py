from foundation.common_types.fqns.fqn import ModuleFqn


class FatherModuleNotExists(Exception):
    def __init__(self, fqn: ModuleFqn, parent_fqn: ModuleFqn):
        self.fqn: ModuleFqn = fqn
        self.parent_fqn: ModuleFqn = parent_fqn
        super().__init__(f"Parent module {parent_fqn} does not exist for {fqn}")
