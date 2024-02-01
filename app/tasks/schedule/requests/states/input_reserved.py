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


from app.db.models import RequestStates, OrderTypes
from app.repositories.request import RequestRepository
from app.tasks import celery_app
from app.utils.calculations.hard import get_need_values_input
from app.utils.decorators.celery_async import celery_sync


@celery_app.task(name='request_state_input_reservation_check')
@celery_sync
async def request_state_input_reservation_check():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT_RESERVATION):
        need_input_value, need_value = await get_need_values_input(request=request, order_type=OrderTypes.INPUT)
        if not need_input_value and not need_value:
            await RequestRepository().update(request, state=RequestStates.INPUT)  # Started next state
            return

        # FIXME (IF ORDER CANCELED, FOUND NEW ORDERS)

    request_state_input_reservation_check.apply_async()
