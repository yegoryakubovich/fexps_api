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


from app.db.models import Rate, Session, RateTypes, RateSources, Method
from app.repositories import CurrencyRepository, RateParseRepository, MethodRepository, RateRepository, \
    CommissionPackRepository, RatePairRepository, CommissionPackValueRepository
from app.services.base import BaseService
from app.utils.calcs.rates.basic.data_rate import calcs_data_rate
from app.utils.calcs.rates.bybit import calcs_rate_bybit
from app.utils.calcs.rates.default import calcs_rate_default
from app.utils.calcs.rates.requisite import calcs_rate_requisite
from app.utils.decorators import session_required
from app.utils.parsers.bybit import parser_bybit_get


class RateService(BaseService):
    model = Rate

    @session_required(permissions=['rates'], can_root=True)
    async def keep_pair_by_task(self, session: Session):
        for commission_pack in await CommissionPackRepository().get_list():
            commissions_packs_values = await CommissionPackValueRepository().get_list(commission_pack=commission_pack)
            for commission_pack_value in commissions_packs_values:
                if commission_pack_value.value_to == 0:
                    input_value = commission_pack_value.value_from + 1_000_00
                else:
                    input_value = round(
                        (commission_pack_value.value_to - commission_pack_value.value_from) /
                        2 + commission_pack_value.value_from
                    )
                input_methods: list[Method] = []
                for input_currency in await CurrencyRepository().get_list():
                    input_methods += [
                        input_method
                        for input_method in await MethodRepository().get_list(currency=input_currency)
                    ]
                output_methods: list[Method] = []
                for output_currency in await CurrencyRepository().get_list():
                    output_methods += [
                        output_method
                        for output_method in await MethodRepository().get_list(currency=output_currency)
                    ]
                for input_method in input_methods:
                    for output_method in output_methods:
                        if input_method.currency.id_str == output_method.currency.id_str:
                            continue
                        result = await calcs_data_rate(
                            input_method=input_method,
                            output_method=output_method,
                            commission_pack=commission_pack,
                            input_value=input_value,
                        )
                        if not result:
                            continue
                        await RatePairRepository().create(
                            commission_pack_value=commission_pack_value,
                            input_method=input_method,
                            output_method=output_method,
                            rate_decimal=result.rate_decimal,
                            rate=result.rate,
                        )
        return {}

    @session_required(permissions=['rates'], can_root=True)
    async def keep_by_task(self, session: Session):
        for method in await MethodRepository().get_list():
            for rate_type in [RateTypes.INPUT, RateTypes.OUTPUT]:
                rate = await calcs_rate_requisite(method=method, rate_type=rate_type)
                source = RateSources.REQUISITE
                rate = None  # turn off requisite rate
                if not rate:
                    rate = await calcs_rate_default(method=method, rate_type=rate_type)
                    source = RateSources.DEFAULT
                if not rate:
                    rate = await calcs_rate_bybit(method=method, rate_type=rate_type)
                    source = RateSources.BYBIT
                if not rate:
                    continue
                await RateRepository().create(method=method, type=rate_type, source=source, rate=rate)
        return {}

    @session_required(permissions=['rates'], can_root=True)
    async def parse_bybit_by_task(self, session: Session):
        currency = await CurrencyRepository().get_by_id_str(id_str='rub')
        for rate_type in [RateTypes.INPUT, RateTypes.OUTPUT]:
            rate = await parser_bybit_get(currency=currency, rate_type=rate_type)
            if not rate:
                continue
            await RateParseRepository().create(
                currency=currency,
                type=rate_type,
                source=RateSources.BYBIT,
                rate=rate,
            )
        return {}
