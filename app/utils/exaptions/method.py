from app.utils import ApiException


class FieldsMissingParams(ApiException):
    pass


class FieldsValidationError(ApiException):
    pass
