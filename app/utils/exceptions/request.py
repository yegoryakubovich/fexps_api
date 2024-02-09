from app.utils import ApiException


class RequestStateWrong(ApiException):
    code = 10000
    message = 'Request.{id_value} has state "{state}", but should have state "{need_state}"'
