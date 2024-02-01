from typing import List

from pydantic import BaseModel


class RequisiteScheme(BaseModel):
    requisite_id: int
    currency_value: int
    value: int
    rate: int


class RequisiteTypeScheme(BaseModel):
    requisites_list: List[RequisiteScheme]
    currency_value: int
    commission_value: int = 0
    div_value: int = 0
    value: int
    rate: int


class AllRequisiteTypeScheme(BaseModel):
    input_requisites: RequisiteTypeScheme
    input_currency_value: int
    input_value: int

    output_requisites: RequisiteTypeScheme
    output_currency_value: int
    output_value: int

    commission_value: int = 0
    div_value: int = 0
    rate: int
