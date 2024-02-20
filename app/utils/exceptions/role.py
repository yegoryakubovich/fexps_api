from .base import ApiException


class RoleAlreadyExist(ApiException):
    code = 8000
    message = 'Role "{id_str}" already exist'

