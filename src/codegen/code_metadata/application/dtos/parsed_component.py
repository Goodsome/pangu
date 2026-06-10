from pydantic import BaseModel
from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_type import ParsedType


class ParsedComponent(BaseModel):
    name: str
    description: str
    bases: list[ParsedType]
    attributes: list[ParsedAttribute]
    behaviors: list[ParsedBehavior]
    imports: list[ImportDto]
    members: list[str]
    discriminator: str | None

    @property
    def is_union(self) -> bool:
        return self.discriminator is not None
