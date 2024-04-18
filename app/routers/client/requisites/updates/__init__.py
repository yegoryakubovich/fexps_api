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
from .disable import router as router_disable
from .enable import router as router_enable
from .stop import router as router_stop
from .value import router as router_confirmation
from .value import router as router_value


router = Router(
    prefix='/updates',
    routes_included=[
        router_stop,
        router_enable,
        router_disable,
        router_value,
    ],
)
