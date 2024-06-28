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


from app.db.models import Method, MethodFieldTypes
from app.utils.exceptions.method import MethodFieldsParameterMissing, MethodFieldsTypeError


async def method_check_validation_scheme(method: Method, fields: dict):
    for field in method.schema_fields:
        field_key = field.get('key')
        field_type = field.get('type')
        field_optional = field.get('optional')
        field_result = fields.get(field_key)
        if not field_result and field_optional:
            continue
        if not field_result:
            raise MethodFieldsParameterMissing(
                kwargs={
                    'field_name': 'fields',
                    'parameter': field_key,
                },
            )
        if field_type == MethodFieldTypes.STR and not isinstance(field_result, str):
            raise MethodFieldsTypeError(
                kwargs={
                    'field_name': 'fields',
                    'param_name': field_key,
                    'type_name': field_type,
                },
            )
        if field_type == MethodFieldTypes.INT and not isinstance(field_result, int):
            raise MethodFieldsTypeError(
                kwargs={
                    'field_name': 'fields',
                    'param_name': field_key,
                    'type_name': field_type,
                },
            )


async def check_input_field(schema_input_fields: list, fields: dict):
    for field in schema_input_fields:
        field_key = field.get('key')
        field_type = field.get('type')
        field_optional = field.get('optional')
        field_result = fields.get(field_key)
        if not field_result and field_optional:
            continue
        if not field_result:
            raise MethodFieldsParameterMissing(
                kwargs={
                    'field_name': 'fields',
                    'parameter': field_key,
                },
            )
        for type_, python_type in [
            (MethodFieldTypes.STR, str),
            (MethodFieldTypes.INT, int),
            (MethodFieldTypes.IMAGE, str),
        ]:
            if field_type == type_ and not isinstance(field_result, python_type):
                raise MethodFieldsTypeError(
                    kwargs={
                        'field_name': 'fields',
                        'param_name': field_key,
                        'type_name': field_type,
                    },
                )
