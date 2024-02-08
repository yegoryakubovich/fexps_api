from app.utils import ApiException


class MethodFieldsMissing(ApiException):
    code = 3000
    message = 'Field {field_name} is missing'


class MethodFieldsParameterMissing(ApiException):
    code = 3001
    message = 'Field {field_name} is missing parameter "{parameter}"'


class MethodParametersMissing(ApiException):
    code = 3002
    message = 'Field {field_name}.{number} mission parameter "{parameter}"'


class MethodParametersValidationError(ApiException):
    code = 3003
    message = 'Field {field_name}.{number}.{param_name} must contain: {parameters}'


class MethodFieldsTypeError(ApiException):
    code = 3004
    message = 'Field {field_name}.{param_name} does not match {type_name}'
