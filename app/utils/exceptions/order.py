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


class OrderRequestFieldsMissing(ApiException):
    code = 5000
    message = 'Field {field_name} is missing'


class OrderRequestAlreadyExists(ApiException):
    code = 5001
    message = 'OrderRequest already exists. OrderRequest.{id_} in state "{state}"'


class OrderStateWrong(ApiException):
    code = 5002
    message = 'Order.{id_value} has state "{state}", but should have state "{need_state}"'


class OrderStateNotPermission(ApiException):
    code = 5003
    message = 'Order.{id_value} you dont have permission to execute "{action}"'


class OrderNotPermission(ApiException):
    code = 5004
    message = '{field}.{id_value} you dont have permission'


class OrderRequestStateNotPermission(ApiException):
    code = 5005
    message = 'OrderRequest.{id_value} you dont have permission to execute "{action}"'
