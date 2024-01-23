from app.utils import ApiException


class OrderRequestValidationError(ApiException):
    pass


class OrderRequestFound(ApiException):
    pass
