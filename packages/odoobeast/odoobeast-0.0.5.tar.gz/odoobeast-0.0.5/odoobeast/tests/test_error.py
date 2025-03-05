import unittest
from core.error import ErrorHandler
import os

class TestErrorHandler(unittest.TestCase):
    def setUp(self):
        self.error_handler = ErrorHandler()
        self.log_file = 'error.log'

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_log_error(self):
        error_message = "Test error message"
        self.error_handler.log_error(error_message)

        with open(self.log_file, 'r') as file:
            log_contents = file.read()

        self.assertIn(error_message, log_contents)

    def test_log_format(self):
        error_message = "Format test error"
        self.error_handler.log_error(error_message)

        with open(self.log_file, 'r') as file:
            log_contents = file.readlines()

        self.assertTrue(any(error_message in line for line in log_contents))

if __name__ == '__main__':
    unittest.main()
