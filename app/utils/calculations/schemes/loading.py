from typing import List

from pydantic import BaseModel


class RequisiteScheme(BaseModel):
    requisite_id: int
    currency_value: int
    value: int
    rate: int


class RequisiteTypeScheme(BaseModel):
    requisites_scheme_list: List[RequisiteScheme]
    sum_currency_value: int
    sum_value: int


class AllRequisiteTypeScheme(BaseModel):
    input_requisite_type: RequisiteTypeScheme
    output_requisites_type: RequisiteTypeScheme
    input_rate: int
    output_rate: int
    commission_value: int
