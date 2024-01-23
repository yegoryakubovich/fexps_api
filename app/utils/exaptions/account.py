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
# class WrongPassword(ApiException):
#     code = 2001
#     message = 'Wrong password'
#
#
# class AccountUsernameExist(ApiException):
#     code = 2002
#     message = 'Account with username "{username}" already exist'
#
#
# class AccountMissingRole(ApiException):
#     code = 2003
#     message = 'There are not enough funds on your balance'
#
#
# class AccountWithUsernameDoeNotExist(ApiException):
#     code = 2004
#     message = 'Account @{username} does not exist'
#
#
# class AccountContactNotFound(ApiException):
#     code = 2104
#     message = 'Account @{username} does not exist'
