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


from pydantic import Field, field_validator, model_validator, BaseModel
from pydantic_core.core_schema import ValidationInfo

from app.db.models import RequestTypes
from app.services import RequestService
from app.utils import Router, Response
from app.utils.exceptions.main import ParametersAllContainError
from app.utils.exceptions.main import ValueMustBePositive, ParameterContainError, ParameterOneContainError

router = Router(
    prefix='/create',

)


class RequestCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    type: str = Field(min_length=1, max_length=8)
    input_method_id: int = Field(default=None)
    input_currency_value: int = Field(default=None)
    input_value: int = Field(default=None)
    output_requisite_data_id: int = Field(default=None)
    output_currency_value: int = Field(default=None)
    output_value: int = Field(default=None)

    @model_validator(mode='after')
    def check_type(self) -> 'RequestCreateSchema':
        if self.type not in RequestTypes.choices:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'type',
                    'parameters': RequestTypes.choices,
                },
            )
        datas = {
            RequestTypes.INPUT: {
                'required': [self.input_method_id],
                'required_names': ['input_method_id'],
                'optional': [self.input_currency_value, self.input_value],
                'optional_names': ['input_currency_value', 'input_value'],
            },
            RequestTypes.OUTPUT: {
                'required': [self.output_requisite_data_id],
                'required_names': ['output_requisite_data_id'],
                'optional': [self.output_currency_value, self.output_value],
                'optional_names': ['output_currency_value', 'output_value'],
            },
            RequestTypes.ALL: {
                'required': [self.input_method_id, self.output_requisite_data_id],
                'required_names': ['input_method_id', 'output_requisite_data_id'],
                'optional': [self.input_currency_value, self.output_currency_value],
                'optional_names': ['input_currency_value', 'output_currency_value'],
            },
        }
        if None in datas[self.type]['required']:
            raise ParametersAllContainError(
                kwargs={
                    'parameters': datas[self.type]["required_names"],
                },
            )
        if (len(datas[self.type]['optional']) - datas[self.type]['optional'].count(None)) != 1:
            raise ParameterOneContainError(
                kwargs={
                    'parameters': datas[self.type]["optional_names"],
                },
            )
        return self

    @field_validator('input_currency_value', 'input_value', 'output_currency_value', 'output_value')
    @classmethod
    def check_values(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(
                kwargs={
                    'field_name': info.field_name,
                },
            )
        return value


@router.post()
async def route(schema: RequestCreateSchema):
    result = await RequestService().create(
        token=schema.token,
        wallet_id=schema.wallet_id,
        type_=schema.type,
        input_method_id=schema.input_method_id,
        input_currency_value=schema.input_currency_value,
        input_value=schema.input_value,
        output_requisite_data_id=schema.output_requisite_data_id,
        output_currency_value=schema.output_currency_value,
        output_value=schema.output_value,
    )
    return Response(**result)
