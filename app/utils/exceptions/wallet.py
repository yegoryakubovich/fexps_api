from .base import ApiException


class WalletLimitReached(ApiException):
    code = 6000
    message = 'Wallet limit reached. Max wallet value {wallet_max_value}'


class WalletCountLimitReached(ApiException):
    code = 6001
    message = 'Wallet count limit reached'


class NotEnoughFundsOnBalance(ApiException):
    code = 6002
    message = 'There are not enough funds on your balance'


class SystemWalletNotExists(ApiException):
    code = 6003
    message = 'System wallet not exists'


class WalletPermissionError(ApiException):
    code = 6004
    message = 'You dont have permission to use the wallet'
