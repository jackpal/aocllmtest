import unittest
from perform import run  # Assuming your code is in a file named perform.py

class TestRunFunction(unittest.TestCase):

    def test_successful_execution(self):
        program = "def solve(part, input): return input.upper()"
        status, result = run(program, 1, "hello", timeout=5)
        self.assertEqual(status, "success")
        self.assertEqual(result, "HELLO")

    def test_successful_execution_with_part(self):
        program = "def solve(part, input): return input[part - 1]"
        status, result = run(program, 2, "abcde", timeout=5)
        self.assertEqual(status, "success")
        self.assertEqual(result, "b")

    def test_error_missing_solve(self):
        program = "def wrong_function(part, input): return 0"
        status, result = run(program, 1, "test", timeout=5)
        self.assertEqual(status, "error")
        self.assertIn("NameError", result)

    def test_error_runtime_exception(self):
        program = "def solve(part, input): return 1 / 0"
        status, result = run(program, 1, "test", timeout=5)
        self.assertEqual(status, "error")
        self.assertIn("ZeroDivisionError", result)

    def test_timeout(self):
        program = "def solve(part, input): import time; time.sleep(2); return 'done'"
        status, result = run(program, 1, "test", timeout=1)  # Timeout less than sleep time
        self.assertEqual(status, "timeout")
        self.assertIsNone(result)

    def test_infinite_loop_timeout(self):
        program = "def solve(part, input): \n  while True: pass"
        status, result = run(program, 1, "test", timeout=1)
        self.assertEqual(status, "timeout")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
