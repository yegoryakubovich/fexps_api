from app.repositories.currency import CurrencyRepository
from app.repositories.request import RequestRepository
from app.utils.calculations.orders import calc_all


async def test_request():
    result_all = await calc_all(
        request=await RequestRepository().get_by_id(id_=6),
        currency_input=await CurrencyRepository().get_by_id(id_=2),
        currency_output=await CurrencyRepository().get_by_id(id_=1),
        input_currency_value=5000000,
    )
    print('#ALL')
    print(f'input_currency_value = {result_all.input_currency_value}')
    print(f'input_value = {result_all.input_value}')
    print(f'output_currency_value = {result_all.output_currency_value}')
    print(f'output_value = {result_all.output_value}')
    print(f'commission_value = {result_all.commission_value}')
    print(f'div_value = {result_all.div_value}')
    print(f'rate = {result_all.rate}')
    print('\n\n')
    for i, calc in enumerate(result_all.input_calc.calc_requisites):
        print(f'INPUT #{i + 1}')
        print(f'currency_value = {calc.currency_value}')
        print(f'value = {calc.value}')
        print(f'rate = {calc.rate}')
    print('\n\n')
    for i, calc in enumerate(result_all.output_calc.calc_requisites):
        print(f'OUTPUT #{i + 1}')
        print(f'currency_value = {calc.currency_value}')
        print(f'value = {calc.value}')
        print(f'rate = {calc.rate}')
    print('\n\n')
