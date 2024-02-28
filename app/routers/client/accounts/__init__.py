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


from .get import router as router_get
from .create import router as router_create
from .check_username import router as router_check_username
from .check_password import router as router_check_password
from .change_password import router as router_change_password
from app.utils import Router


router = Router(
    prefix='/accounts',
    routes_included=[
        router_get,
        router_create,
        router_check_username,
        router_change_password,
        router_check_password,
    ],
    tags=['Accounts'],
)
