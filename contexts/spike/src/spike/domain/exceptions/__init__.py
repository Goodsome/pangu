class InternalError(Exception):
    """Raised when an internal operation fails and technical details should be hidden from callers."""

    __cause__: BaseException | None

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.__cause__ = cause
