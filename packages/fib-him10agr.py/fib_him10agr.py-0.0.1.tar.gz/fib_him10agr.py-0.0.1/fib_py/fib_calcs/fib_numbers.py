from typing import List
from .fib_number import fib_num

def calculate_numbers(numbers: List[int]) -> List[int]:

    return [fib_num(i) for i in numbers]