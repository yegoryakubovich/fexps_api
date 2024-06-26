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


from fastapi import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.repositories import TextRepository, FileKeyRepository
from app.utils import Router


router = Router(
    prefix='/upload',
)


@router.get(response_class=HTMLResponse)
async def route(
        request: Request,
        key: str,
):
    if not await FileKeyRepository().get(file_id=None, key=key):
        return
    text_add_file = await TextRepository().get_by_key_or_none(key='file_add_button')
    text_continue = await TextRepository().get_by_key_or_none(key='file_continue_button')
    return Jinja2Templates(directory="app/utils/templates").TemplateResponse(
        request=request,
        name="file/upload.html",
        context={
            'title': 'Finance Express',
            'key': key,
            'text_add_file': text_add_file,
            'text_continue': text_continue,
        },
    )
