from pydantic import Field
from codegen.code_metadata.domain.value_objects.gherkin_step import GherkinStep
from codegen.shared.domain.core.value_object import ValueObject


class Scenario(ValueObject):
    """Gherkin 场景，由名称和有序步骤列表组成。"""

    name: str
    steps: list[GherkinStep] = Field(default_factory=list)
