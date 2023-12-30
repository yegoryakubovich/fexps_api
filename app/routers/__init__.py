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


from .favicon import router as router_favicon
from .accounts import router as router_accounts
from .sessions import router as router_sessions
from .languages import router as router_languages
from .methods import router as router_methods
from .requisite import router as router_requisite
from .countries import router as router_countries
from .currencies import router as router_currencies
from .timezones import router as router_timezones
from .contacts import router as router_contacts
from .roles import router as router_roles
from .texts import router as router_texts


routers = [
    router_favicon,
    router_accounts,
    router_sessions,
    router_languages,
    router_methods,
    router_requisite,
    router_countries,
    router_currencies,
    router_timezones,
    router_contacts,
    router_roles,
    router_texts,
]
