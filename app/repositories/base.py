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


from peewee import DoesNotExist

from app.db.models.base import BaseModel
from app.utils import ApiException


class ModelDoesNotExist(ApiException):
    pass


class BaseRepository:
    model: BaseModel
    model_name: str

    def __init__(self, model: BaseModel = None):
        if model:
            self.model = model

    async def get_list(self) -> list[BaseModel]:
        return self.model.select().where(self.model.is_deleted == False).execute()

    async def get_by_id(self, id_: int) -> BaseModel:
        try:
            model = self.model.get(
                (self.model.id == id_) &
                (self.model.is_deleted == False)
            )
            return model
        except DoesNotExist:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')

    async def get_by_id_str(self, id_str: str) -> BaseModel:
        try:
            self.model = self.model.get(
                (self.model.id_str == id_str) &
                (self.model.is_deleted == False)
            )
            return self.model
        except DoesNotExist:
            raise ModelDoesNotExist(f'{self.model.__name__} "{id_str}" does not exist')
