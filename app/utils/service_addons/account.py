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


from app.db.models import Account
from app.utils.crypto import create_hash_by_string_and_salt
from app.utils.exceptions import AccountWrongPassword


async def account_is_correct_password(account: Account, password: str) -> bool:
    if account.password_hash == await create_hash_by_string_and_salt(
            string=password,
            salt=account.password_salt,
    ):
        return True
    else:
        raise AccountWrongPassword()


async def account_check_password(
        account: Account,
        password: str,
) -> dict:
    await account_is_correct_password(account=account, password=password)

    return True
