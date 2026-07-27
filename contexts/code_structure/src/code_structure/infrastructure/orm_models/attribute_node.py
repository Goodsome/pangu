from code_structure.infrastructure.orm_models.member_node import MemberNode


class AttributeNode(MemberNode):
    name: str
    fqn: str

