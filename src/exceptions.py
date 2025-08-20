from http import HTTPStatus


class NotFoundPostError(Exception):
    def __init__(self, message: str="Post Not Found", status_code: int = HTTPStatus.NOT_FOUND) -> None:
        self.message = message
        self.status_code = status_code