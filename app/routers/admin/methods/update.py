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

from pydantic import Field, BaseModel, field_validator

from app.db.models import MethodFieldTypes
from app.services import MethodService
from app.utils import Response, Router
from app.utils.exceptions import MethodParametersMissing, MethodParametersValidationError, MethodFieldsMissing

router = Router(
    prefix='/update',
)


class MethodUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    currency_id_str: Optional[str] = Field(default=None, min_length=2, max_length=32)
    fields: Optional[list[dict]] = Field(default=None)
    input_fields: Optional[list[dict]] = Field(default=None)
    rate_input_default: Optional[int] = Field(default=None)
    rate_output_default: Optional[int] = Field(default=None)
    rate_input_percent: Optional[int] = Field(default=None)
    rate_output_percent: Optional[int] = Field(default=None)
    color: str = Field(min_length=2, max_length=7, default='#1D1D1D')
    bgcolor: str = Field(min_length=2, max_length=7, default='#FFFCEF')
    is_rate_default: Optional[bool] = Field(default=None)


    @field_validator('fields')
    @classmethod
    def fields_valid(cls, fields):
        if isinstance(fields, str):
            raise MethodFieldsMissing(kwargs={'field_name': 'fields'})
        for i, field in enumerate(fields, start=1):
            for key in ['key', 'type', 'name', 'optional']:
                if field.get(key) is None:
                    raise MethodParametersMissing(
                        kwargs={
                            'field_name': 'fields',
                            'number': i,
                            'parameter': key,
                        },
                    )
            if not isinstance(field.get('optional'), bool):
                raise MethodParametersValidationError(
                    kwargs={
                        'field_name': 'fields',
                        'number': i,
                        'param_name': 'optional',
                        'parameters': ['true', 'false'],
                    },
                )
            if field.get('type') not in MethodFieldTypes.choices_field:
                raise MethodParametersValidationError(
                    kwargs={
                        'field_name': 'fields',
                        'number': i,
                        'param_name': 'type',
                        'parameters': MethodFieldTypes.choices_field,
                    },
                )
        return fields

    @field_validator('input_fields')
    @classmethod
    def input_fields_valid(cls, input_fields):
        if isinstance(input_fields, str):
            raise MethodFieldsMissing(kwargs={'field_name': 'input_fields'})
        for i, field in enumerate(input_fields, start=1):
            for key in ['key', 'type', 'name', 'optional']:
                if field.get(key) is None:
                    raise MethodParametersMissing(
                        kwargs={
                            'field_name': 'input_fields',
                            'number': i,
                            'parameter': key,
                        },
                    )
            if not isinstance(field.get('optional'), bool):
                raise MethodParametersValidationError(
                    kwargs={
                        'field_name': 'input_fields',
                        'number': i,
                        'param_name': 'optional',
                        'parameters': ['true', 'false'],
                    },
                )
            if field.get('type') not in MethodFieldTypes.choices:
                raise MethodParametersValidationError(
                    kwargs={
                        'field_name': 'input_fields',
                        'number': i,
                        'param_name': 'type',
                        'parameters': MethodFieldTypes.choices,
                    },
                )
        return input_fields


@router.post()
async def route(schema: MethodUpdateSchema):
    result = await MethodService().update_by_admin(
        token=schema.token,
        id_=schema.id_,
        currency_id_str=schema.currency_id_str,
        fields=schema.fields,
        input_fields=schema.input_fields,
        rate_input_default=schema.rate_input_default,
        rate_output_default=schema.rate_output_default,
        rate_input_percent=schema.rate_input_percent,
        rate_output_percent=schema.rate_output_percent,
        color=schema.color,
        bgcolor=schema.bgcolor,
        is_rate_default=schema.is_rate_default,
    )
    return Response(**result)
