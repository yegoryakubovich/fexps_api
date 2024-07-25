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


def value_to_float(value: Optional[int], decimal: int = 2) -> Optional[float]:
    if isinstance(value, str):
        value = value.replace(',', '.')
    if not value and value != 0:
        return
    return float(value) / (10 ** decimal)


def value_to_int(value: Optional[float], decimal: int = 2, round_method=round) -> Optional[int]:
    if not value and value != 0:
        return
    return round_method(value * (10 ** decimal))


def value_to_str(value: Optional[float]) -> Optional[str]:
    if isinstance(value, str):
        value = value.replace(',', '.')
    if not value and value != 0:
        return ''
    return f'{float(value):_}'.replace('_', ' ')
