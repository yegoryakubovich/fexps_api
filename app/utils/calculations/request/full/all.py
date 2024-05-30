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

from app.db.models import RequestFirstLine, RequestTypes, Wallet, Method
from app.repositories import CommissionPackValueRepository, WalletRepository
from app.utils.calculations.request.commissions import get_commission_value_input, \
    get_commission_value_output
from app.utils.calculations.request.full.input import calc_request_full_input
from app.utils.calculations.request.full.output import calc_request_full_output
from app.utils.calculations.request.rates import get_rate_by_input
from app.utils.calculations.schemes.loading import AllTypeScheme


async def get_commission(
        first_line: str,
        wallet_id: int,
        value: int,
) -> int:
    wallet = await WalletRepository().get_by_id(id_=wallet_id)
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=wallet.commission_pack,
        value=value,
    )
    if first_line in RequestFirstLine.choices_input:
        return get_commission_value_input(value=value, commission_pack_value=commission_pack_value)
    elif first_line in RequestFirstLine.choices_output:
        return get_commission_value_output(value=value, commission_pack_value=commission_pack_value)


def get_auto_rate(
        first_line: str,
        type_: str,
        rate_decimal: int,
        currency_value: int,
        value: int,
) -> int:
    if type_ == RequestTypes.ALL and first_line in RequestFirstLine.choices_output:
        return get_rate_by_input(
            currency_value=currency_value,
            value=value,
            rate_decimal=rate_decimal,
        )
    return get_rate_by_input(
        currency_value=currency_value,
        value=value,
        rate_decimal=rate_decimal,
    )


async def calc_request_full_all(
        wallet: Wallet,
        input_method: Method,
        output_method: Method,
        first_line_value: int,
        first_line: str,
        type_: str,
        rate_decimal: int,
) -> Optional[AllTypeScheme]:
    currency_value = first_line_value
    input_result_type, output_result_type = None, None
    input_rate, output_rate = None, None
    if first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
        input_result_type = await calc_request_full_input(
            first_line=first_line,
            input_method=input_method,
            rate_decimal=rate_decimal,
            wallet_id=wallet.id,
            currency_value=currency_value,
        )
        if not input_result_type:
            return
        input_rate = get_auto_rate(
            first_line=first_line,
            type_=type_,
            rate_decimal=rate_decimal,
            currency_value=input_result_type.currency_value,
            value=input_result_type.value,
        )
        output_from_value = input_result_type.value - input_result_type.commission_value
        output_result_type = await calc_request_full_output(
            output_method=output_method,
            rate_decimal=rate_decimal,
            value=output_from_value,
        )
        if not output_result_type:
            return
        output_rate = get_auto_rate(
            first_line=first_line,
            type_=type_,
            rate_decimal=rate_decimal,
            currency_value=output_result_type.currency_value,
            value=output_result_type.value,
        )
    elif first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
        output_result_type = await calc_request_full_output(
            output_method=output_method,
            rate_decimal=rate_decimal,
            currency_value=currency_value,
        )
        if not output_result_type:
            return
        output_rate = get_auto_rate(
            first_line=first_line,
            type_=type_,
            rate_decimal=rate_decimal,
            currency_value=output_result_type.currency_value,
            value=output_result_type.value,
        )
        commission_value = await get_commission(
            first_line=first_line,
            wallet_id=wallet.id,
            value=output_result_type.value,
        )
        input_from_value = output_result_type.value + commission_value
        input_result_type = await calc_request_full_input(
            first_line=first_line,
            input_method=input_method,
            rate_decimal=rate_decimal,
            wallet_id=wallet.id,
            value=input_from_value,
        )
        if not input_result_type:
            return
        input_rate = get_auto_rate(
            first_line=first_line,
            type_=type_,
            rate_decimal=rate_decimal,
            currency_value=input_result_type.currency_value,
            value=input_result_type.value,
        )
    commission_value = input_result_type.commission_value + output_result_type.commission_value
    return AllTypeScheme(
        input_type=input_result_type,
        output_type=output_result_type,
        input_rate=input_rate,
        output_rate=output_rate,
        commission_value=commission_value,
    )
