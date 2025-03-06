import argparse
from fib_py.fib_calcs import fib_num

def fib_numb() -> None:

    parser = argparse.ArgumentParser(
        description="Calculate fibonaccci numbers"
    )

    parser.add_argument("--number", action='store',
                        type=int, required=True,
                        help="Fibonacci number to be calculated")
    args = parser.parse_args()
    print(f"Fibonacci number is: {fib_num(number=args.number)}")

if __name__ == "__main__":

    fib_numb()