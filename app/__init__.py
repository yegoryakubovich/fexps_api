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


import logging

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.init_db import init_db
from app.routers import routers
from app.utils.client import init
from app.utils.logger import config_logger
from app.utils.middleware import Middleware
from app.utils.validation_error import validation_error
from config import settings


async def on_startup():
    try:
        await init_db()
        logging.info('Success connect to database')
    except ConnectionRefusedError:
        logging.error('Failed to connect to database')
        exit(1)

    # from app.test import start_test
    # await start_test()


app = FastAPI(
    title='Finance Express API',
    version=settings.version,
    contact={
        'name': 'Yegor Yakubovich',
        'url': 'https://yegoryakubovich.com',
        'email': 'personal@yegoryakubovich.com',
    },
    license_info={
        'name': 'Apache 2.0',
        'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
    },
    dependencies=[Depends(init)],
    exception_handlers={RequestValidationError: validation_error},
    on_startup=[on_startup],
)
app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=Middleware())
[app.include_router(router) for router in routers]


def create_app():
    config_logger()
    logging.info(msg='Application starting...')
    return app
