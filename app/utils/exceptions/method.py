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


from .base import ApiException


class MethodFieldsMissing(ApiException):
    code = 3000
    message = 'Field {field_name} is missing'


class MethodFieldsParameterMissing(ApiException):
    code = 3001
    message = 'Field {field_name} is missing parameter "{parameter}"'


class MethodParametersMissing(ApiException):
    code = 3002
    message = 'Field {field_name}.{number} mission parameter "{parameter}"'


class MethodParametersValidationError(ApiException):
    code = 3003
    message = 'Field {field_name}.{number}.{param_name} must contain: {parameters}'


class MethodFieldsTypeError(ApiException):
    code = 3004
    message = 'Field {field_name}.{param_name} does not match {type_name}'
