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


from .account import WrongPassword, InvalidUsername, AccountWithUsernameDoeNotExist, AccountMissingPermission, \
    AccountContactsAlreadyExists, InvalidPassword
from .base import ApiException
from .commission_pack import CommissionIntervalAlreadyTaken, CommissionIntervalValidationError, IntervalNotExistsError
from .image import InvalidFileType, TooLargeFile
from .main import ModelDoesNotExist, NotEnoughPermissions, NoRequiredParameters, ParameterContainError, \
    ParameterOneContainError, ParameterTwoContainError, ParametersAllContainError, ValueMustBePositive, WrongToken, \
    WrongTokenFormat, MethodNotSupportedRoot, ModelAlreadyExist
from .method import MethodFieldsMissing, MethodFieldsParameterMissing, MethodParametersMissing, \
    MethodParametersValidationError, MethodFieldsTypeError
from .order import OrderRequestFieldsMissing, OrderRequestAlreadyExists, OrderStateWrong, OrderStateNotPermission, \
    OrderNotPermission
from .request import RequestStateWrong, RequestStateNotPermission
from .requisite import RequisiteMinimumValueError
from .role import RoleAlreadyExist
from .text import TextDoesNotExist, TextAlreadyExist, TextPackDoesNotExist, TextTranslationDoesNotExist, \
    TextTranslationAlreadyExist
from .wallet import WalletLimitReached, WalletCountLimitReached, NotEnoughFundsOnBalance, SystemWalletNotExists, \
    WalletPermissionError
