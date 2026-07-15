from dataclasses import dataclass

from foundation.message_bus.message_bus import BaseMessageBus

from code_dom.application.commands.generate_code import GenerateCodeCommand
from code_dom.domain.aggregates.code_document import CodeDocument


@dataclass
class CodeDomApi:
    message_bus: BaseMessageBus

    def save_documents(self, documents: list[CodeDocument]):
        cmd = GenerateCodeCommand(code_documents=documents)
        self.message_bus.handle(cmd)
