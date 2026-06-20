from architecture.infrastructure.unit_of_work import UnitOfWork
from codegen.shared.infrastructure.message_bus import BaseMessageBus

MessageBus = BaseMessageBus[UnitOfWork]