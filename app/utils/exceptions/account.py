from .base import ApiException


class WrongPassword(ApiException):
    code = 2000
    message = 'Wrong password'


class InvalidUsername(ApiException):
    code = 2001
    message = 'Invalid username. The correct username starts with a letter and can contain numbers or underscores'


class AccountWithUsernameDoeNotExist(ApiException):
    code = 2002
    message = 'Account @{username} does not exist'


class AccountMissingPermission(ApiException):
    code = 2003
    message = 'Account has no "{id_str}" permission'


class AccountContactsAlreadyExists(ApiException):
    code = 2004
    message = 'Account Contact has already exists'


class InvalidPassword(ApiException):
    code = 2005
    message = 'Invalid password. The correct password must contain at least one lowercase letter, one uppercase ' \
              'letter, one digit and one special character, and include between 6 and 32 characters.'

