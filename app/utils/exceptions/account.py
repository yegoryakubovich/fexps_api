from .base import ApiException


class AccountWrongPassword(ApiException):
    code = 2000
    message = 'Wrong password'


class AccountUsernameExist(ApiException):
    code = 2001
    message = 'Account with username "{username}" already exist'


class AccountWithUsernameDoeNotExist(ApiException):
    code = 2002
    message = 'Account @{username} does not exist'


class AccountMissingRole(ApiException):
    code = 2003
    message = 'Account has no "{id_str}" permission'


class AccountContactsAlreadyExists(ApiException):
    code = 2004
    message = 'Account Contact has already exists'
