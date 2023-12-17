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


from app.services import AccountRoleService
from app.services.session_get_by_token import SessionGetByTokenService


def session_required(
        return_model: bool = True,
        return_account: bool = False,
        permissions: list[str] = None,
        can_guest: bool = False,
):
    def inner(function):
        async def wrapper(*args, **kwargs):
            session = kwargs.get('session')
            token = kwargs.get('token')
            if token or 'token' in kwargs.keys():
                kwargs.pop('token')

            if not session and not can_guest or (token and can_guest):
                session = await SessionGetByTokenService().execute(token=token)

            if return_model:
                if return_account:
                    kwargs['account'] = session.account
                else:
                    kwargs['session'] = session

                for permission in permissions or []:
                    await AccountRoleService().check_permission(account=session.account, id_str=permission)

            return await function(*args, **kwargs)
        return wrapper
    return inner
