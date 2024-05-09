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

from app.db.models import Request, RateTypes
from app.repositories import RateRepository
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.calculations.schemes.loading import TypesScheme

custom_logger = RequestLogger(prefix='request_state_loading_output_check')


async def request_type_output(
        request: Request,
        currency_value=None,
        value=None,
) -> Optional[TypesScheme]:
    currency = request.output_method.currency
    custom_logger.info(
        text=f'first_line={request.first_line}, currency={currency.id_str}',
        request=request,
    )
    last_rate = await RateRepository().get(currency=currency, type=RateTypes.OUTPUT)
    if not last_rate:
        return
    request_rate = last_rate.value
    if currency.rate_decimal != request.rate_decimal:
        request_rate *= 10 ** (request.rate_decimal - currency.rate_decimal)
    if currency_value:
        value = round(currency_value / (request_rate / 10 ** request.rate_decimal))
    elif value:
        currency_value = round(value * (request_rate / 10 ** request.rate_decimal))
    if None in [currency_value, value]:
        return
    return TypesScheme(currency_value=currency_value, value=value, commission_value=0)
