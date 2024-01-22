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


from pydantic import Field, field_validator

from app.db.models import MethodFieldTypes
from app.services import MethodService
from app.services.method import FieldsMissingParams, FieldsValidationError
from app.utils import BaseSchema
from app.utils import Router, Response

router = Router(
    prefix='/create',
)


class MethodCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    currency: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=1, max_length=1024)
    fields: list[dict] = Field(
        default='[{"key": "string", "type": "str/int", "name": "string", "optional": false}]'
    )
    confirmation_fields: list[dict] = Field(
        default='[{"key": "string", "type": "str/int/image", "name": "string", "optional": false}]'
    )

    @field_validator('fields')
    @classmethod
    def fields_valid(cls, fields):
        for i, field in enumerate(fields, start=1):
            for key in ['key', 'type', 'name', 'optional']:
                if field.get(key) is None:
                    raise FieldsMissingParams(f'fields.{i} missing parameter "{key}"')
            if not isinstance(field.get('optional'), bool):
                raise FieldsValidationError(
                    f'fields.{i}.type must contain true/false'
                )
            if field.get('type') not in [MethodFieldTypes.STR, MethodFieldTypes.INT]:
                raise FieldsValidationError(
                    f'fields.{i}.type must contain {MethodFieldTypes.STR}/{MethodFieldTypes.INT}'
                )
        return fields

    @field_validator('confirmation_fields')
    @classmethod
    def confirmation_fields_valid(cls, confirmation_fields):
        if isinstance(confirmation_fields, str):
            raise FieldsMissingParams(f'confirmation_fields missing')
        for i, field in enumerate(confirmation_fields, start=1):
            for key in ['key', 'type', 'name', 'optional']:
                if field.get(key) is None:
                    raise FieldsMissingParams(f'confirmation_fields.{i} missing parameter "{key}"')
            if not isinstance(field.get('optional'), bool):
                raise FieldsValidationError(
                    f'fields.{i}.type must contain true/false'
                )
            if field.get('type') not in [MethodFieldTypes.STR, MethodFieldTypes.INT]:
                raise FieldsValidationError(
                    f'confirmation_fields.{i}.type must contain '
                    f'{MethodFieldTypes.STR}/{MethodFieldTypes.INT}/{MethodFieldTypes.IMAGE}'
                )
        return confirmation_fields


@router.post()
async def route(schema: MethodCreateSchema):
    result = await MethodService().create(
        token=schema.token,
        currency_id_str=schema.currency,
        name=schema.name,
        fields=schema.fields,
        confirmation_fields=schema.confirmation_fields,
    )

    return Response(**result)
