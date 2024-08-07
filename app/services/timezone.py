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


from app.db.models import Timezone, Session, Actions
from app.repositories import TimezoneRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import ModelAlreadyExist


class TimezoneService(BaseService):
    model = Timezone

    @session_required(permissions=['timezones'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            deviation: int,
    ):
        if await TimezoneRepository().is_exist_by_id_str(id_str=id_str):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Timezone',
                    'id_type': 'id_str',
                    'id_value': id_str,
                }
            )
        timezone = await TimezoneRepository().create(
            id_str=id_str,
            deviation=deviation
        )
        await self.create_action(
            model=timezone,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id_str': timezone.id_str,
                'deviation': timezone.deviation,
                'by_admin': True,
            },
            with_client=True,
        )
        return {
            'id_str': timezone.id_str,
        }

    async def get(self, id_str: str):
        timezone = await TimezoneRepository().get_by_id_str(id_str=id_str)
        return {
            'timezone': await self.generate_transfer_dict(timezone=timezone),
        }

    async def get_list(self) -> dict:
        timezones = {
            'timezones': [
                await self.generate_transfer_dict(timezone=timezone)
                for timezone in await TimezoneRepository().get_list()
            ],
        }
        return timezones

    @session_required(permissions=['timezones'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        timezone = await TimezoneRepository().get_by_id_str(id_str=id_str)
        await TimezoneRepository().delete(model=timezone)
        await self.create_action(
            model=timezone,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )
        return {}

    @staticmethod
    async def generate_transfer_dict(timezone: Timezone) -> dict:
        return {
            'id': timezone.id,
            'id_str': timezone.id_str,
            'deviation': timezone.deviation,
        }
