from codegen.code_metadata.domain.enums.gherkin_keyword import GherkinKeyword
from codegen.shared.domain.core.value_object import ValueObject


class GherkinStep(ValueObject):
    """Gherkin 场景中的单一步骤，由关键字和步骤文本组成。"""

    keyword: GherkinKeyword
    text: str
