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


from app.db.models import RequestStates, OrderTypes, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import TransferSystemService
from app.tasks import celery_app
from app.utils.calculations.hard import get_need_values_input
from app.utils.decorators.celery_async import celery_sync


@celery_app.task()
def request_state_input_check_smart_start():
    name = 'request_state_input_check'
    actives = celery_app.control.inspect().active()
    for worker in actives:
        for task in actives[worker]:
            if task['name'] == name:
                return
    request_state_input_check.apply_async()


@celery_app.task(name='request_state_input_check')
@celery_sync
async def request_state_input_check():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT):
        need_input_value, need_value = await get_need_values_input(request=request, order_type=OrderTypes.INPUT)
        if need_input_value or need_value:
            await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)  # Back to previous state
            return
        if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.RESERVE):
            return  # Found payment reserve
        if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.PAYMENT):
            return  # Found payment orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.CONFIRMATION):
            return  # Found confirmation orders

        await TransferSystemService().payment_commission(request=request)
        await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)  # Started next state

    request_state_input_check.apply_async()
