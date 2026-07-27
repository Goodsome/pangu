from code_structure.infrastructure.orm_models.member_node import MemberNode


class MethodNode(MemberNode):
    name: str
    fqn: str

