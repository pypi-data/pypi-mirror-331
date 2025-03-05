class CeleryException(Exception):
    __slots__ = ["status_code", "detail"]

    status_code: int
    detail: str

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.status_code, self.detail)

    def __reduce__(self) -> tuple[type, tuple[int, str]]:
        return self.__class__, (self.status_code, self.detail)
