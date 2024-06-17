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
from .calculate import router as router_calc
from .create import router as router_create
from .get import router as router_get
from .search import router as router_search
from .updates import router as router_update


router = Router(
    prefix='/requests',
    routes_included=[
        router_create,
        router_calc,
        router_get,
        router_search,
        router_update,
    ],
    tags=['Requests'],
)
