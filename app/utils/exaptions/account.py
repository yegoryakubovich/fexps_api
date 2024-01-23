from app.utils import ApiException


class WrongPassword(ApiException):
    pass


class AccountUsernameExist(ApiException):
    pass


class AccountMissingRole(ApiException):
    pass


class AccountWithUsernameDoeNotExist(ApiException):
    pass


class AccountContactNotFound(ApiException):
    pass
