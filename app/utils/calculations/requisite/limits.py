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

from app.db.models import Requisite


def check_currency_value_limits(requisite: Requisite, currency_value: int) -> Optional[int]:
    if requisite.currency_value_min:
        if currency_value < requisite.currency_value_min:
            return
    if requisite.currency_value_max:
        if currency_value > requisite.currency_value_max:
            return requisite.currency_value_max
    if requisite.currency.div:
        if currency_value < requisite.currency.div:
            return
    if currency_value > requisite.currency_value:
        return requisite.currency_value
    return currency_value


def check_value_limits(requisite: Requisite, value: int) -> Optional[int]:
    if requisite.value_min:
        if value < requisite.value_min:
            return
    if requisite.value_max:
        if value > requisite.value_max:
            return requisite.value_max
    if value > requisite.value:
        return requisite.value
    return value
