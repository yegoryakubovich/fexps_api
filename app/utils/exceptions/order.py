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
