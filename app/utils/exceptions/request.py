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


class RequestStateWrong(ApiException):
    code = 10000
    message = 'Request.{id_value} has state "{state}", but should have state "{need_state}"'


class RequestStateNotPermission(ApiException):
    code = 10001
    message = 'Request.{id_value} you dont have permission to execute "{action}"'


class RequestRateNotFound(ApiException):
    code = 10002
    message = 'Rate pair {input_method}-{output_method} not found'


class RequestFoundOrders(ApiException):
    code = 10003
    message = 'Request.{id_value} found not completed/cancelled orders'
