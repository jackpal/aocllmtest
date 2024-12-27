# test_perform.py
import unittest
from perform import run

class TestPerform(unittest.TestCase):

    def test_successful_execution(self):
        program = "import sys\nprint(sys.stdin.read())"
        input_str = "test input"
        status, output = run(program, input_str, 2)
        self.assertEqual(status, 'success')
        self.assertEqual(output, input_str)

    def test_program_with_output(self):
        program = "print('hello world')"
        status, output = run(program, "", 2)
        self.assertEqual(status, 'success')
        self.assertEqual(output, 'hello world')

    def test_program_with_integer_output(self):
        program = "print(123)"
        status, output = run(program, "", 2)
        self.assertEqual(status, 'success')
        self.assertEqual(output, '123')

    def test_program_with_error(self):
        program = "undefined_variable"
        status, output = run(program, "", 2)
        self.assertEqual(status, 'error')
        self.assertIn("NameError", output)

    def test_program_with_syntax_error(self):
        program = "print("
        status, output = run(program, "", 2)
        self.assertEqual(status, 'error')
        self.assertIn("SyntaxError", output)

    def test_program_timeout(self):
        program = "import time\nwhile True:\n    time.sleep(0.1)"
        status, output = run(program, "", 1)
        self.assertEqual(status, 'timeout')
        self.assertIsNone(output)

    def test_program_reads_empty_stdin(self):
        program = "import sys\nprint(len(sys.stdin.read()))"
        status, output = run(program, "", 2)
        self.assertEqual(status, 'success')
        self.assertEqual(output, '0')

    def test_program_with_multiline_output(self):
        program = "print('line1')\nprint('line2')"
        status, output = run(program, "", 2)
        self.assertEqual(status, 'success')
        self.assertEqual(output, 'line1\nline2')

if __name__ == '__main__':
    unittest.main()
