class HTTPRequestException(Exception):

    def __init__(self, status_code: int, response_message: str = None) -> None:
        self.status_code = status_code
        self.response_message = response_message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, response_message={self.response_message!r})"
