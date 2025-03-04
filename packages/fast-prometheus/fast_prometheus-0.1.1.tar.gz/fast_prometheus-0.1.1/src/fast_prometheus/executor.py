from dataclasses import dataclass

from starlette.requests import Request
from starlette.responses import Response


@dataclass
class BeforeData:
    request: Request
    path: str
    method: str
    start_time: float


@dataclass
class AfterData:
    request: Request
    response: Response
    start_time: float
    method: str
    path: str
    status_code: int


@dataclass
class ErrorData:
    reques: Request
    start_time: float
    method: str
    path: str
    status_code: int = 500


class Executor:
    def before_execute(self, data: BeforeData) -> None:
        pass

    def after_execute(self, data: AfterData) -> None:
        pass

    def error_execute(self, data: ErrorData) -> None:
        pass
