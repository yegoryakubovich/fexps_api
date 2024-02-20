from .base import ApiException


class TextDoesNotExist(ApiException):
    code = 9000
    message = 'Text with key "{key}" does not exist'


class TextAlreadyExist(ApiException):
    code = 9001
    message = 'Text with key "{key}" already exist'


class TextPackDoesNotExist(ApiException):
    code = 9002
    message = 'TextPack with language "{language_name}" does not exist'


class TextTranslationDoesNotExist(ApiException):
    code = 9003
    message = 'Text translation with language "{id_str}" does not exist'


class TextTranslationAlreadyExist(ApiException):
    code = 9004
    message = 'Text translation with language "{id_str}" already exist'
