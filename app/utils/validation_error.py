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


from json import loads, dumps
from urllib.request import Request

from fastapi.exceptions import RequestValidationError

from app.utils.response import Response, ResponseState


async def validation_error(_: Request, exception: RequestValidationError):
    try:
        json = loads(dumps(exception.args))
    except AttributeError:
        json = exception

    return Response(
        state=ResponseState.error,
        message='Validation error',
        json=json,
    )
