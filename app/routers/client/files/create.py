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


from typing import Annotated, List

from fastapi import UploadFile, Form
from starlette.responses import HTMLResponse

from app.services import FileService
from app.utils import Router


router = Router(
    prefix='/create',
)


@router.post(response_class=HTMLResponse)
async def route(
        key: Annotated[str, Form()],
        files: Annotated[List[UploadFile], Form()],
):
    result = await FileService().create(key=key, files=files)
    text = 'Готово! Вы можете вернуться'
    if result.get('error') and result['error'] == 'key_not_found':
        text = 'Ошибка. Ваш ключ уже был использован.'
    html_content = """
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Центрированный текст</title>
        <style>
            body, html {
                height: 100%;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #f0f0f0;
            }
            .centered {
                font-size: 48px;
                font-family: Arial, sans-serif;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="centered">center_text</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content.replace('center_text', text))
