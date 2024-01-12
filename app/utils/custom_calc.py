import math


def round_floor(number: float, decimal: int = 2):
    return math.floor(number * 10 ** decimal) / 10 ** decimal


def round_ceil(number: float, decimal: int = 2):
    return math.ceil(number * 10 ** decimal) / 10 ** decimal


def minus(num1: [int, float], num2: [int, float], decimal: int = 2):
    return round(num1 - num2, decimal)


def plus(num1: [int, float], num2: [int, float], decimal: int = 2):
    return round(num1 + num2, decimal)
