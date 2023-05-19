from typing import Any

def equal_to(value: Any):
    return lambda i: i == value

def greater_than(value: float):
    return lambda i: i > value

def less_than(value: float):
    return lambda i: i < value

def between(start: float, end: float):
    return lambda i: i >= start and i <= end

def one_of(*values: Any):
    return lambda i: i in values