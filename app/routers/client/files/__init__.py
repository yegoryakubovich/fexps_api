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
from .create import router as router_create
from .get import router as router_get
from .open import router as router_open
from .upload import router as router_upload
from .keys import router as router_keys


router = Router(
    prefix='/files',
    routes_included=[
        router_upload,
        router_create,
        router_get,
        router_open,
        router_keys,
    ],
    tags=['Files'],
)
