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


from .account import AccountService, WrongPassword
from .account_contact import AccountContactService
from .account_role import AccountRoleService
from .action import ActionService
from .commission_pack import CommissionPackService
from .commission_pack_value import CommissionPackValueService
from .contact import ContactService
from .country import CountryService
from .currency import CurrencyService
from .language import LanguageService
from .method import MethodService
from .order import OrderService
from .order_states_canceled import OrderStatesCanceledService
from .order_states_completed import OrderStatesCompletedService
from .order_states_confirmation import OrderStatesConfirmationService
from .order_states_payment import OrderStatesPaymentService
from .order_states_reserve import OrderStatesReserveService
from .request import RequestService
from .requisite import RequisiteService
from .requisite_data import RequisiteDataService
from .role import RoleService
from .session import SessionService
from .session_get_by_token import SessionGetByTokenService
from .text import TextService
from .text_pack import TextPackService
from .text_translation import TextTranslationService
from .timezone import TimezoneService
from .transfer import TransferService
from .wallet import WalletService
from .wallet_account import WalletAccountService


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
