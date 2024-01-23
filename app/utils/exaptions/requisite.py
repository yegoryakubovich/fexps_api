from app.utils import ApiException


class NotRequiredParams(ApiException):
    pass


class MinimumTotalValueError(ApiException):
    pass
