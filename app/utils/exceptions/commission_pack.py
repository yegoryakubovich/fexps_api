from app.utils import ApiException


class CommissionIntervalAlreadyTaken(ApiException):
    code = 4000
    message = 'This interval already taken'


class CommissionIntervalValidationError(ApiException):
    code = 4001
    message = 'The field value_to must be greater than value_from'

