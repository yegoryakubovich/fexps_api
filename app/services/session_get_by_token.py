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


from addict import Dict

from app.repositories import SessionRepository
from app.db.models import Session
from app.services.base import BaseService
from app.utils.crypto import create_hash_by_string_and_salt
from config import settings


class SessionGetByTokenService(BaseService):
    @staticmethod
    async def execute(token: str) -> Session | Dict:
        # Get session ID and token
        try:
            session_id_str, token = token.split(':')
        except ValueError:
            raise WrongTokenFormat()
        session_id = int(session_id_str)

        if session_id == 0:
            if token == settings.root_token:
                session_dict = {
                    'id': 0,
                    'account': {
                        'id': 0,
                        'username': 'root',
                        'firstname': 'root',
                        'lastname': 'root',
                        'surname': None,
                        'country_id': {'id_str': 'root'},
                        'language_id': {'id_str': 'root'},
                        'timezone_id': {'id_str': 'root'},
                        'currency_id': {'id_str': 'root'},
                        'is_deleted': False,
                    },
                    'is_deleted': False,
                }
                return Dict(**session_dict)
            else:
                raise WrongToken()

        session: Session = await SessionRepository().get_by_id(id_=session_id)
        if session.token_hash == await create_hash_by_string_and_salt(
            string=token,
            salt=session.token_salt,
        ):
            return session
        else:
            raise WrongToken('Wrong token')
