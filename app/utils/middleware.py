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


from json import loads

from fastapi import Request
from pydantic import ValidationError

from app.utils import ApiException
from app.utils.response import ResponseState, Response
from app.utils.validation_error import validation_error
from app.utils.value import value_replace


class Middleware:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except ApiException as e:
            response = Response(
                state=ResponseState.error,
                error={
                    'code': e.code,
                    'kwargs': e.kwargs,
                    'message': value_replace(e.message, **e.kwargs),
                }
            )
        except ValidationError as e:
            response = await validation_error(_=request, exception=loads(e.json()))
        return response
