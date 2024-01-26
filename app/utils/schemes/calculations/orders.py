from typing import List

from pydantic import BaseModel


class CalcRequisiteScheme(BaseModel):
    requisite_id: int
    currency_value: int
    value: int
    rate: int


class CalcOrderScheme(BaseModel):
    calc_requisites: List[CalcRequisiteScheme]
    currency_value: int
    value: int
    rate: int


class CalcAllOrderScheme(BaseModel):
    input_calc: CalcOrderScheme
    output_calc: CalcOrderScheme
    input_currency_value: int
    input_value: int
    output_currency_value: int
    output_value: int
    rate: int
