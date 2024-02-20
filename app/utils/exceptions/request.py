from .base import ApiException


class RequestStateWrong(ApiException):
    code = 10000
    message = 'Request.{id_value} has state "{state}", but should have state "{need_state}"'


class RequestStateNotPermission(ApiException):
    code = 10001
    message = 'Request.{id_value} you dont have permission to execute "{action}"'
