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

from .language import Language
from .currency import Currency
from .timezone import Timezone
from .base import BaseModel
from .text import Text


class Country(BaseModel):
    id = PrimaryKeyField()
    id_str = CharField(max_length=16)
    name_text = ForeignKeyField(model=Text)
    language_default = ForeignKeyField(model=Language, null=True)
    timezone_default = ForeignKeyField(model=Timezone, null=True)
    currency_default = ForeignKeyField(model=Currency, null=True)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'countries'
