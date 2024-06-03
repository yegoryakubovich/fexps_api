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


from typing import Optional

from pydantic import Field, model_validator, BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

from app.db.models import RequestTypes
from app.services import RequestService
from app.utils import Response, Router
from app.utils.exceptions import ValueMustBePositive
from app.utils.exceptions.main import ParameterContainError, ParameterOneContainError, ParametersAllContainError


router = Router(
    prefix='/calc',
)


class RequestCalcSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    type_: str = Field(min_length=1, max_length=8)
    input_currency_id_str: Optional[str] = Field(min_length=1, max_length=8, default=None)
    output_currency_id_str: Optional[str] = Field(min_length=1, max_length=8, default=None)

    @model_validator(mode='after')
    def check_type(self) -> 'RequestCalcSchema':
        if self.type_ not in RequestTypes.choices:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'type_',
                    'parameters': RequestTypes.choices,
                },
            )
        datas = {
            RequestTypes.INPUT: {
                'required': [self.input_currency_id_str],
                'required_names': ['input_currency_id_str'],
            },
            RequestTypes.OUTPUT: {
                'required': [self.output_currency_id_str],
                'required_names': ['output_currency_id_str'],
            },
            RequestTypes.ALL: {
                'required': [self.input_currency_id_str, self.output_currency_id_str],
                'required_names': ['input_currency_id_str', 'output_currency_id_str'],
            },
        }
        if None in datas[self.type_]['required']:
            raise ParametersAllContainError(
                kwargs={
                    'parameters': datas[self.type_]["required_names"],
                },
            )
        return self


@router.post()
async def route(schema: RequestCalcSchema):
    result = await RequestService().calc(
        token=schema.token,
        type_=schema.type_,
        input_currency_id_str=schema.input_currency_id_str,
        output_currency_id_str=schema.output_currency_id_str,
    )
    return Response(**result)
