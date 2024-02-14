from app.utils import ApiException


class OrderRequestFieldsMissing(ApiException):
    code = 5000
    message = 'Field {field_name} is missing'


class OrderRequestAlreadyExists(ApiException):
    code = 5001
    message = 'Order request already exists. order_request.{id_} in state "{state}"'


class OrderStateWrong(ApiException):
    code = 5002
    message = 'Order.{id_value} has state "{state}", but should have state "{need_state}"'


class OrderStateNotPermission(ApiException):
    code = 5003
    message = 'Order.{id_value} you dont have permission to execute "{action}"'


class OrderNotPermission(ApiException):
    code = 5004
    message = '{field}.{id_value} you dont have permission'
