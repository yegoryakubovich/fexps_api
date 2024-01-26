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


from app.db.models import Session, Request, Actions, RequestStates
from app.repositories.request import RequestRepository
from app.services import RequestService
from app.services.base import BaseService
from app.utils.decorators import session_required


class RequestStatesInputReservationService(BaseService):
    model = Request

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        request = await RequestRepository().get_by_id(id_=id_)
        await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': RequestStates.INPUT_RESERVATION,
            },
        )
        await RequestService().check_all_orders(request=request)

        return {}
