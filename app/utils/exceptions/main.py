from .base import ApiException


class ModelDoesNotExist(ApiException):
    code = 1000
    message = '{model} with {id_type} "{id_value}" does not exist'


class NotEnoughPermissions(ApiException):
    code = 1001
    message = 'Not enough permissions to execute'


class NoRequiredParameters(ApiException):
    code = 1002
    message = 'One of the following parameters must be filled in: {parameters}'


class ParameterContainError(ApiException):
    code = 1003
    message = 'The field "{field_name}" must contain : {parameters}'


class ParameterOneContainError(ApiException):
    code = 1004
    message = 'Must contain at least one parameter: {parameters}'


class ParameterTwoContainError(ApiException):
    code = 1005
    message = 'Must contain two parameters: {parameters}'


class ParametersAllContainError(ApiException):
    code = 1006
    message = 'All these parameters must be present: {parameters}'


class ValueMustBePositive(ApiException):
    code = 1007
    message = 'The field "{field_name}" must be positive'


class WrongToken(ApiException):
    code = 1008
    message = 'Wrong token'


class WrongTokenFormat(ApiException):
    code = 1009
    message = 'Token does not match format'
