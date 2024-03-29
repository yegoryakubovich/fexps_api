# #
# # (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
# #
#
#
# from typing import Optional
#
# from app.db.models import Request, OrderStates
# from app.db.models import Requisite
# from app.repositories.order import OrderRepository
#
#
# async def get_need_values_input(request: Request, order_type: str) -> tuple[Optional[int], Optional[int]]:
#     result_currency_value, result_value = request.input_currency_value, request.input_value
#     for order in await OrderRepository().get_list(request=request, type=order_type):
#         if order.state == OrderStates.CANCELED:
#             continue
#         if request.input_currency_value:
#             result_currency_value = round(result_currency_value - order.currency_value)
#         if request.input_value:
#             result_value = round(result_value - order.value)
#     if result_value and request.commission_value:
#         result_value = round(result_value - request.commission_value)
#     return result_currency_value, result_value
#
#
# async def get_need_values_output(request: Request, order_type: str) -> tuple[Optional[int], Optional[int]]:
#     result_currency_value, result_value = request.output_currency_value, request.output_value
#     for order in await OrderRepository().get_list(request=request, type=order_type):
#         if order.state == OrderStates.CANCELED:
#             continue
#         if request.output_currency_value:
#             result_currency_value = round(result_currency_value - order.currency_value)
#         if request.output_value:
#             result_value = round(result_value - order.value)
#     if result_value and request.commission_value:
#         result_value = round(result_value - request.commission_value)
#     return result_currency_value, result_value
#
#
# def suitability_check_currency_value(
#         need_currency_value: int,
#         requisite: Requisite,
#         currency_div: int,
#         rate_decimal: int,
#         order_type: str,
# ) -> Optional[tuple[int, int]]:
#     needed_currency_value = need_currency_value
#     # requisite_rate = round(requisite.rate / 10 ** requisite.currency.rate_decimal * 10 ** rate_decimal)
#     # if check_zero(needed_currency_value, requisite.currency_value):
#     #     return
#     # if requisite.value_min and needed_currency_value < requisite.value_min:
#     #     return
#     # if requisite.value_max and needed_currency_value > requisite.value_max:
#     #     needed_currency_value = requisite.value_max
#     # if needed_currency_value < currency_div:
#     #     return
#     # if requisite.currency_value >= needed_currency_value:
#     #     suitable_currency_value = needed_currency_value
#     # else:
#     #     suitable_currency_value = requisite.currency_value
#     # suitable_currency_value, suitable_value = get_div_values(
#     #     currency_value=suitable_currency_value,
#     #     rate=requisite_rate,
#     #     rate_decimal=rate_decimal,
#     #     div=currency_div,
#     #     type_=order_type,
#     # )
#     # if not suitable_currency_value or not suitable_value:
#     #     return
#     #
#     # return suitable_currency_value, suitable_value
#
#
# def suitability_check_value(
#         need_value: int,
#         requisite: Requisite,
#         currency_div: int,
#         rate_decimal: int,
#         order_type: str,
# ) -> Optional[tuple[int, int]]:
#     needed_value = need_value
#     # requisite_rate = round(requisite.rate / 10 ** requisite.currency.rate_decimal * 10 ** rate_decimal)
#     # if check_zero(needed_value, requisite.value):
#     #     return
#     # if requisite.value_min and needed_value < requisite.value_min:  # Меньше минимума
#     #     return
#     # if requisite.value_max and needed_value > requisite.value_max:  # Больше максимума
#     #     needed_value = requisite.value_max
#     # if round(needed_value * requisite_rate / 10 ** rate_decimal) < currency_div:
#     #     return
#     # if requisite.value >= needed_value:
#     #     suitable_value = needed_value
#     # else:
#     #     suitable_value = requisite.value
#     # suitable_currency_value, suitable_value = get_div_values(
#     #     value=suitable_value, rate=requisite_rate, rate_decimal=rate_decimal, div=currency_div, type_=order_type,
#     # )
#     # if not suitable_currency_value or not suitable_value:
#     #     return
#     #
#     # return suitable_currency_value, suitable_value
