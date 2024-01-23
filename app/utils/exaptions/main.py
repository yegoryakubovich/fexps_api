from app.utils import ApiException


class DoesNotPermission(ApiException):
    pass


class ModelDoesNotExist(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class DataValidationError(ApiException):
    pass

#
# class DoesNotPermission(ApiException):
#     code = 3001
#     message = 'Wallet limit reached. Max wallet value {wallet_max_value}'
#
#
# class ModelDoesNotExist(ApiException):
#     code = 3002
#     message = '{model_name}.{id_} does not exist'
#
# class NoRequiredParameters(ApiException):
#     code = 3003
#     message = 'Error following parameters: {params}'
#
#
# class DataValidationError(ApiException):
#     code = 3004
#     message = 'There are not enough funds on your balance'
