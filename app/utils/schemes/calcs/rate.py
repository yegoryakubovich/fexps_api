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


from pydantic import BaseModel


class DataRateScheme(BaseModel):
    rate: int
    rate_decimal: int


class RequisiteItemScheme(BaseModel):
    requisite_id: int
    currency_value: int
    value: int


class RequisiteDataScheme(BaseModel):
    requisite_items: list[RequisiteItemScheme]
    currency_value: int
    rate: int
    value: int
