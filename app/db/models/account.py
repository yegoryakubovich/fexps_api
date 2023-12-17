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


from peewee import PrimaryKeyField, CharField, ForeignKeyField, BooleanField

from .base import BaseModel
from .country import Country
from .currency import Currency
from .language import Language
from .timezone import Timezone


class Account(BaseModel):
    id = PrimaryKeyField()
    username = CharField(max_length=32)
    password_salt = CharField(max_length=32)
    password_hash = CharField(max_length=32)
    firstname = CharField(max_length=32)
    lastname = CharField(max_length=32)
    surname = CharField(max_length=32, null=True)
    country = ForeignKeyField(model=Country)
    language = ForeignKeyField(model=Language)
    timezone = ForeignKeyField(model=Timezone)
    currency = ForeignKeyField(model=Currency)
    is_active = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'accounts'
