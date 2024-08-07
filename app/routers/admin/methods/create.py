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


from pydantic import Field, BaseModel, field_validator

from app.db.models import MethodFieldTypes
from app.services.method import MethodService
from app.utils import Router, Response
from app.utils.exceptions.method import MethodParametersMissing, MethodParametersValidationError

router = Router(
    prefix='/create',
)


class MethodCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    currency: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=1, max_length=1024)
    fields: list[dict] = Field(
        default='[{"key": "string", "type": "str/int", "name": "string", "optional": false}]'
    )
    input_fields: list[dict] = Field(
        default='[{"key": "string", "type": "str/int/image", "name": "string", "optional": false}]'
    )
    input_rate_default: int = Field(default=0)
    output_rate_default: int = Field(default=0)
    input_rate_percent: int = Field(default=0)
    output_rate_percent: int = Field(default=0)
    color: str = Field(min_length=2, max_length=7, default='#1D1D1D')
    bgcolor: str = Field(min_length=2, max_length=7, default='#FFFCEF')
    is_rate_default: bool = Field(default=False)

    @field_validator('fields')
    @classmethod
    def fields_valid(cls, fields):
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
            if field.get('type') not in [MethodFieldTypes.INT, MethodFieldTypes.STR]:
                raise MethodParametersValidationError(
                    kwargs={
                        'field_name': 'fields',
                        'number': i,
                        'param_name': 'type',
                        'parameters': [MethodFieldTypes.INT, MethodFieldTypes.STR],
                    },
                )
        return fields

    @field_validator('input_fields')
    @classmethod
    def input_fields_valid(cls, input_fields):
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
            if field.get('type') not in [MethodFieldTypes.INT, MethodFieldTypes.STR, MethodFieldTypes.IMAGE]:
                raise MethodParametersValidationError(
                    kwargs={
                        'field_name': 'input_fields',
                        'number': i,
                        'param_name': 'type',
                        'parameters': [MethodFieldTypes.INT, MethodFieldTypes.STR, MethodFieldTypes.IMAGE],
                    },
                )

        return input_fields


@router.post()
async def route(schema: MethodCreateSchema):
    result = await MethodService().create_by_admin(
        token=schema.token,
        currency_id_str=schema.currency,
        name=schema.name,
        fields=schema.fields,
        input_fields=schema.input_fields,
        input_rate_default=schema.input_rate_default,
        output_rate_default=schema.output_rate_default,
        input_rate_percent=schema.input_rate_percent,
        output_rate_percent=schema.output_rate_percent,
        color=schema.color,
        bgcolor=schema.bgcolor,
        is_rate_default=schema.is_rate_default,
    )
    return Response(**result)
