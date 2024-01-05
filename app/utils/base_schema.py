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


from decimal import Decimal

from pydantic import BaseModel, field_validator, Field

from app.utils.exception import ApiException


class ValueMustBePositive(ApiException):
    pass


class BaseSchema(BaseModel):
    pass


class BaseValueSchema(BaseSchema):
    value: Decimal = Field(decimal_places=2)

    @field_validator('value')
    @classmethod
    def check_value(cls, value):
        if value <= 0:
            raise ValueMustBePositive('The value must be positive')
        return float(value)
