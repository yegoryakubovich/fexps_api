#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from .account_role import AccountRoleService
from .action import ActionService
from .account import AccountService, WrongPassword
from .role import RoleService
from .session import SessionService
from .country import CountryService
from .language import LanguageService
from .session_get_by_token import SessionGetByTokenService
from .text_translation import TextTranslationService
from .timezone import TimezoneService
from .currency import CurrencyService
from .text import TextService
from .text_pack import TextPackService
from .method import MethodService
from .contact import ContactService
from .account_contact import AccountContactService
from .requisite_data import RequisiteDataService
from .wallet import WalletService
from .wallet_account import WalletAccountService
from .transfer import TransferService
from .requisite import RequisiteService
from .request import RequestService
from .order import OrderService
from .commission_pack import CommissionPackService
from .commission_pack_value import CommissionPackValueService


"""
create
check
get
get list
search
update
delete
*other*
"""