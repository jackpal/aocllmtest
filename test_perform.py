import unittest
from perform import run

class TestPerform(unittest.TestCase):

    def test_successful_execution(self):
        program = "print('Hello, world!')"
        status, output = run(program, '', [], 5)
        self.assertEqual(status, 'success')
        self.assertEqual(output.strip(), 'Hello, world!')

    def test_execution_with_input(self):
        program = "import sys\nprint(sys.stdin.read().strip())"
        status, output = run(program, 'test input', [], 5)
        self.assertEqual(status, 'success')
        self.assertEqual(output.strip(), 'test input')

    def test_execution_with_arguments(self):
        program = "import sys\nprint(' '.join(sys.argv[1:]))"
        status, output = run(program, '', ['arg1', 'arg2'], 5)
        self.assertEqual(status, 'success')
        self.assertEqual(output.strip(), 'arg1 arg2')

    def test_program_with_error(self):
        program = "1 / 0"
        status, error = run(program, '', [], 5)
        self.assertEqual(status, 'error')
        self.assertIn('ZeroDivisionError', error)

    def test_program_timeout(self):
        program = "import time\nwhile True:\n    time.sleep(0.1)"
        status, output = run(program, '', [], 1)
        self.assertEqual(status, 'timeout')
        self.assertIsNone(output)

    def test_example_call(self):
        status, output = run("import sys\nprint(sys.stdin.read())", 'abc', [], 10)
        self.assertEqual(status, 'success')
        self.assertEqual(output.strip(), 'abc')

if __name__ == '__main__':
    unittest.main()
