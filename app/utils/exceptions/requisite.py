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


class RequisiteMinimumValueError(ApiException):
    code = 7000
    message = 'Minimum value = {access_change_balance}'


class RequisiteActiveOrdersExistsError(ApiException):
    code = 7001
    message = 'Requisite.{id_value} has active orders, unable to execute "{action}"'


class RequisiteStateWrong(ApiException):
    code = 7002
    message = 'Requisite.{id_value} has state "{state}", but should have state "{need_state}"'


class RequisiteNotEnough(ApiException):
    code = 7003
    message = 'Requisite.{id_value} insufficient funds, max value = {value}'
