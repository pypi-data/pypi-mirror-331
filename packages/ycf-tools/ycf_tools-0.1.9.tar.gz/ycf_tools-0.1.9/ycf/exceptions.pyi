from _typeshed import Incomplete

class MultiBaseException(BaseException):
    message: Incomplete
    exs: Incomplete
    def __init__(self, message: str, exs: list[BaseException]) -> None: ...
