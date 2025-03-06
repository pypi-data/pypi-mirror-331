from typing import Optional

def fib_num(number: int) -> Optional[int]:

    if number < 0 :
        return None
    elif number <= 1:
        return number
    else:
        return fib_num(number - 1) + fib_num(number - 2)
