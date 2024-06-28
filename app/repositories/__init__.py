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


from .account import AccountRepository
from .account_contact import AccountContactRepository
from .account_role import AccountRoleRepository
from .action import ActionRepository
from .action_parameter import ActionParameterRepository
from .commission_pack import CommissionPackRepository
from .commission_pack_value import CommissionPackValueRepository
from .contact import ContactRepository
from .country import CountryRepository
from .currency import CurrencyRepository
from .file import FileRepository
from .file_key import FileKeyRepository
from .language import LanguageRepository
from .message import MessageRepository
from .message_file import MessageFileRepository
from .method import MethodRepository
from .notification_history import NotificationHistoryRepository
from .notification_setting import NotificationSettingRepository
from .order import OrderRepository
from .order_file import OrderFileRepository
from .order_request import OrderRequestRepository
from .order_transfer import OrderTransferRepository
from .permission import PermissionRepository
from .rate import RateRepository
from .rate_pair import RatePairRepository
from .rate_parse import RateParseRepository
from .request import RequestRepository
from .request_requisite import RequestRequisiteRepository
from .requisite import RequisiteRepository
from .requisite_data import RequisiteDataRepository
from .role import RoleRepository
from .role_permission import RolePermissionRepository
from .session import SessionRepository
from .session import SessionRepository
from .telegram_post import TelegramPostRepository
from .text import TextRepository
from .text_pack import TextPackRepository
from .text_translation import TextTranslationRepository
from .timezone import TimezoneRepository
from .transfer import TransferRepository
from .transfer_system import TransferSystemRepository
from .wallet import WalletRepository
from .wallet_account import WalletAccountRepository
from .wallet_ban import WalletBanRepository
from .wallet_ban_request import WalletBanRequestRepository
from .wallet_ban_requisite import WalletBanRequisiteRepository
