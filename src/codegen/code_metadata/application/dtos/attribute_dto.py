from pydantic import BaseModel
from codegen.code_metadata.application.dtos.type_def_dto import TypeDefDto


class AttributeDto(BaseModel):
    name: str
    description: str
    type: TypeDefDto
