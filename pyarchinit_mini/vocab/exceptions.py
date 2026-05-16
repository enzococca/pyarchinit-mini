class VocabError(Exception):
    """Base for vocab errors."""


class VocabBootstrapError(VocabError):
    def __init__(self, msg: str, *, hint: str | None = None) -> None:
        super().__init__(msg)
        self.hint = hint


class VocabSchemaError(VocabError):
    def __init__(self, *, path: str, line: int, column: int, msg: str) -> None:
        super().__init__(f"{msg} at {path} line {line}, column {column}")
        self.path = path
        self.line = line
        self.column = column


class VocabUnavailableError(VocabError):
    def __init__(self, *, reason: str) -> None:
        super().__init__(f"vocab unavailable: {reason}")
        self.reason = reason
