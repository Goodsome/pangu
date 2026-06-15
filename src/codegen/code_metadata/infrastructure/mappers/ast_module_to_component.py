import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_module import ParsedDirectoryModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_attribute import (
    AstNodeToAttribute,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import (
    AstNodeToParsedType,
)
from codegen.code_metadata.infrastructure.mappers.ast_to_behavior_mixin import (
    AstToBehaviorMixin,
)

logger = logging.getLogger(__name__)
