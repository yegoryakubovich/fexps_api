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


from app.tasks.schedule.requests.orders_checks import request_new_order_check_smart_start
from app.tasks.schedule.requests.states.input import request_state_input_check_smart_start
from app.tasks.schedule.requests.states.input_reserved import request_state_input_reservation_check_smart_start
from app.tasks.schedule.requests.states.loading import request_state_loading_check_smart_start
from app.tasks.schedule.requests.states.output import request_state_output_check_smart_start
from app.tasks.schedule.requests.states.output_reserved import request_state_output_reservation_check_smart_start
from app.tasks.schedule.requests.states.waiting import request_state_waiting_check_smart_start
from app.utils import Router, Response


router = Router(
    prefix='/start',
)


@router.post()
async def route():
    request_new_order_check_smart_start.apply_async()
    request_state_loading_check_smart_start.apply_async()
    request_state_waiting_check_smart_start.apply_async()
    request_state_input_reservation_check_smart_start.apply_async()
    request_state_input_check_smart_start.apply_async()
    request_state_output_reservation_check_smart_start.apply_async()
    request_state_output_check_smart_start.apply_async()
    return Response()
