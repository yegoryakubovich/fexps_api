from app.utils import ApiException


class RequestStateWrong(ApiException):
    code = 10000
    message = 'Request.{id_} has state "{state}", but should have state "{need_state}"'
