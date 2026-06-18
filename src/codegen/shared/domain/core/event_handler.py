from collections.abc import Iterable

from codegen.shared.domain.core.command import Command
from codegen.shared.domain.core.event import Event


class BaseEventHandler[T_UOW]:
    def __call__(self, event: Event, uow: T_UOW) -> Iterable[Command]: ...
