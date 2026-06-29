from foundation.common_types.identities.module_id import ModuleId


def str_to_module_id(s: str) -> ModuleId:
    return ModuleId.reconstitute(s)