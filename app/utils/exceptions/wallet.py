#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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
