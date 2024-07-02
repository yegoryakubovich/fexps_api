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
from .send_image import router as router_send_image
from .send_notification import router as router_send_notification
from .update_image import router as router_update_image


router = Router(
    prefix='/telegrams',
    routes_included=[
        router_send_image,
        router_send_notification,
        router_update_image,
    ],
    tags=['Telegrams'],
)
