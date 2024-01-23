from app.utils import ApiException


class TextDoesNotExist(ApiException):
    pass


class TextExist(ApiException):
    pass


class TextPackDoesNotExist(ApiException):
    pass


class TextTranslationDoesNotExist(ApiException):
    pass


class TextTranslationExist(ApiException):
    pass
