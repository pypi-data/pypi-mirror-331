class MultiBaseException(BaseException):
    def __init__(self, message: str, exs: list[BaseException]) -> None:
        self.message = message
        self.exs = exs

    def __str__(self) -> str:
        return '{}: [{}]'.format(self.message, ','.join([str(i) for i in self.exs]))
