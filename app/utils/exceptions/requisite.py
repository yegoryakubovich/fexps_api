from .base import ApiException


class RequisiteMinimumValueError(ApiException):
    code = 7000
    message = 'Minimum value = {access_change_balance}'
