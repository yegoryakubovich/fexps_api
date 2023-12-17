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


from app.repositories import SessionRepository
from app.db.models import Session
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.crypto import create_hash_by_string_and_salt


class WrongToken(ApiException):
    pass


class WrongTokenFormat(ApiException):
    pass


class SessionGetByTokenService(BaseService):
    @staticmethod
    async def execute(token: str) -> Session:
        # Get session ID and token
        try:
            session_id_str, token = token.split(':')
        except ValueError:
            raise WrongTokenFormat('Token does not match format')
        session_id = int(session_id_str)

        session: Session = await SessionRepository().get_by_id(id_=session_id)
        if session.token_hash == await create_hash_by_string_and_salt(
            string=token,
            salt=session.token_salt,
        ):
            return session
        else:
            raise WrongToken('Wrong token')
