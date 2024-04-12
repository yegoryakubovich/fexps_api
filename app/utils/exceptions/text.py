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


class TextDoesNotExist(ApiException):
    code = 9000
    message = 'Text with key "{key}" does not exist'


class TextAlreadyExist(ApiException):
    code = 9001
    message = 'Text with key "{key}" already exist'


class TextPackDoesNotExist(ApiException):
    code = 9002
    message = 'TextPack with language "{language_name}" does not exist'


class TextTranslationDoesNotExist(ApiException):
    code = 9003
    message = 'Text translation with language "{id_str}" does not exist'


class TextTranslationAlreadyExist(ApiException):
    code = 9004
    message = 'Text translation with language "{id_str}" already exist'
