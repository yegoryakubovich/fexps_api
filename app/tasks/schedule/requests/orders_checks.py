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

from app.db.models import RequestStates, Actions, Request, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import ActionService
from app.tasks import celery_app
from app.utils.decorators.celery_async import celery_sync
from config import settings


@celery_app.task()
def request_new_order_check_smart_start():
    name = 'request_new_order_check'
    actives = celery_app.control.inspect().active()
    for worker in actives:
        for task in actives[worker]:
            if task['name'] == name:
                return
    request_new_order_check.apply_async()


@celery_app.task(name='request_new_order_check')
@celery_sync
async def request_new_order_check():
    time_now = datetime.utcnow()
    for request in await RequestRepository().get_list_by_asc(state=RequestStates.WAITING):
        request_action = await ActionService().get_action(request, action=Actions.UPDATE)
        if time_now - request_action.datetime >= timedelta(minutes=settings.request_wait_minutes):
            await request_set_state_canceled(request=request)
    request_new_order_check.apply_async()


async def request_set_state_canceled(request: Request) -> None:
    for order in await OrderRepository().get_list(request=request):
        await OrderRepository().update(order, state=OrderStates.CANCELED)
    await RequestRepository().update(request, state=RequestStates.CANCELED)
