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


from app.utils import Router
from .accounts import router as router_accounts
from .commissions_packs import router as router_commissions_packs
from .contacts import router as router_contacts
from .countries import router as router_countries
from .currencies import router as router_currencies
from .images import router as router_images
from .languages import router as router_languages
from .methods import router as router_methods
from .orders import router as router_orders
from .permissions import router as router_permissions
from .roles import router as router_roles
from .texts import router as router_texts
from .timezones import router as router_timezones
from .wallets import router as router_wallets


router = Router(
    prefix='/admin',
    routes_included=[
        router_accounts,
        router_commissions_packs,
        router_contacts,
        router_countries,
        router_currencies,
        router_images,
        router_languages,
        router_methods,
        router_orders,
        router_permissions,
        router_roles,
        router_texts,
        router_timezones,
        router_wallets,
    ],
)
