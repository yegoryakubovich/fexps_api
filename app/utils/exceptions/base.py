class ApiException(Exception):
    code: int = 0
    message: str
    kwargs: dict = {}

    def __init__(self, message: str = None, kwargs: dict = None):
        if not kwargs:
            kwargs = {}
        self.kwargs = kwargs
        if message:
            self.message = message
