import json
from typing import Union

from httpx import Response


class ResponseWrapper:
    """
    Custom Serialization/Deserialization class of Response objects to use in redis.
    """

    # random delimiter, just to make sure this won't be found anywhere in the response.text saved
    DELIMITER = "--__-8__-_-"

    def __init__(self, status_code: int, text: str) -> None:
        self.status_code = status_code
        self.text = text

    def json(self) -> dict:
        return json.loads(self.text)

    def dumps(self) -> str:
        return f"{self.status_code}{self.DELIMITER}{self.text}"

    @classmethod
    def loads(cls, value: str) -> "ResponseWrapper":
        status_code, text = value.split(cls.DELIMITER)
        return cls(int(status_code), text)

    @classmethod
    def from_response(cls, response: Response) -> "ResponseWrapper":
        return cls(status_code=response.status_code, text=response.text)


def _is_server_error(code):
    return 500 <= code <= 599


def filter_5xx_errors(res: Union[Response, ResponseWrapper]) -> bool:
    return not _is_server_error(res.status_code)
