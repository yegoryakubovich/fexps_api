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


from app.db.models import Session
from app.repositories import LanguageRepository
from app.services.text_pack import TextPackService
from app.services.base import BaseService
from app.utils.exceptions import ModelAlreadyExist
from app.utils.decorators import session_required


class LanguageService(BaseService):
    @session_required(permissions=['languages'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            name: str,
    ):
        if await LanguageRepository().is_exist_by_id_str(id_str=id_str):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Language',
                    'id_type': 'id_str',
                    'id_value': id_str,
                }
            )

        language = await LanguageRepository().create(
            id_str=id_str,
            name=name,
        )

        await self.create_action(
            model=language,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': language.id_str,
                'name': language.name,
                'by_admin': True,
            },
            with_client=True,
        )

        await TextPackService().create_by_admin(session=session, language_id_str=language.id_str)
        return {'id_str': language.id_str}

    @session_required(permissions=['languages'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        language = await LanguageRepository().get_by_id_str(id_str=id_str)

        await LanguageRepository().delete(model=language)

        await self.create_action(
            model=language,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get(
            id_str: str,
    ):
        language = await LanguageRepository().get_by_id_str(id_str=id_str)
        return {
            'language': {
                'id': language.id,
                'id_str': language.id_str,
                'name': language.name,
            }
        }

    @staticmethod
    async def get_list() -> dict:
        languages = {
            'languages': [
                {
                    'id': language.id,
                    'id_str': language.id_str,
                    'name': language.name,
                }
                for language in await LanguageRepository().get_list()
            ],
        }
        return languages
