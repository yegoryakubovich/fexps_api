from typing import List

from pydantic import BaseModel


class RequisiteScheme(BaseModel):
    requisite_id: int
    currency_value: int
    value: int
    rate: int


class AllRequisiteTypeScheme(BaseModel):
    input_requisites: List[RequisiteScheme]
    output_requisites: List[RequisiteScheme]
