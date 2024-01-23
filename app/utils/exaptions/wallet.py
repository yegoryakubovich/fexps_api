from app.utils import ApiException


class WalletLimitReached(ApiException):
    pass


class NotEnoughFundsOnBalance(ApiException):
    pass

#
# class WalletLimitReached(ApiException):
#     code = 3001
#     message = 'Wallet limit reached. Max wallet value {wallet_max_value}'
#
#
# class NotEnoughFundsOnBalance(ApiException):
#     code = 3002
#     message = 'There are not enough funds on your balance'
