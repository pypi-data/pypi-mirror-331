from unittest import main, TestCase
from fib_py.fib_calcs.fib_number import fib_num

class RecurringFibNumberTest(TestCase):

    def test_zero(self):

        self.assertEqual(0,fib_num(number=0))
    
    def test_negative(self):

        self.assertEqual(None, fib_num(number=-1))

    def test_one(self):

        self.assertEqual(1, fib_num(number=1))
    
    def test_two(self):

        self.assertEqual(1, fib_num(number=2))
    
    def test_twenty(self):

        self.assertEqual(6765, fib_num(number=20))

if __name__ == "__main__":

    main()