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


from .base import ApiException


class WrongPassword(ApiException):
    code = 2000
    message = 'Wrong password'


class InvalidUsername(ApiException):
    code = 2001
    message = 'Invalid username. The correct username starts with a letter and can contain numbers or underscores'


class AccountWithUsernameDoeNotExist(ApiException):
    code = 2002
    message = 'Account @{username} does not exist'


class AccountMissingPermission(ApiException):
    code = 2003
    message = 'Account has no "{id_str}" permission'


class AccountContactsAlreadyExists(ApiException):
    code = 2004
    message = 'Account Contact has already exists'


class InvalidPassword(ApiException):
    code = 2005
    message = 'Invalid password. The correct password must contain at least one lowercase letter, one uppercase ' \
              'letter, one digit and one special character, and include between 6 and 32 characters.'

