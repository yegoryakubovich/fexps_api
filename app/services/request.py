#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from app.db.models import Session, Request
from app.repositories.request import RequestRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class RequestService(BaseService):
    model = Request

    @session_required()  # FIXME
    async def create(
            self,
            session: Session,
    ) -> dict:
        request = await RequestRepository().create(
        )
        await self.create_action(
            model=request,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id': request.id,
            },
        )
        return {'request_id': request.id}
