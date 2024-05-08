from typing import Optional


def value_to_float(value: Optional[int], decimal: int = 2) -> Optional[float]:
    if isinstance(value, str):
        value = value.replace(',', '.')
    if not value and value != 0:
        return
    return float(value) / (10 ** decimal)
