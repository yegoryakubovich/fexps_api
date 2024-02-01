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


from datetime import datetime, timedelta

from app.db.models import RequestStates, Actions
from app.repositories.request import RequestRepository
from app.services import ActionService
from app.tasks import celery_app
from app.utils.decorators.celery_async import celery_sync
from config import settings


@celery_app.task()
@celery_sync
async def request_new_order_check():
    time_now = datetime.utcnow()
    for request in await RequestRepository().get_list_by_asc(state=RequestStates.WAITING):
        request_action = await ActionService().get_action(request, action=Actions.CREATE)
        if time_now - request_action.datetime >= timedelta(minutes=settings.request_wait_minutes):
            await RequestRepository().update(request, state=RequestStates.CANCELED)
