import unittest
from core.response import ResponseGenerator

class TestResponseGenerator(unittest.TestCase):

    def setUp(self):
        self.response_generator = ResponseGenerator()

    def test_generate_response_happy(self):
        response = self.response_generator.generate_response('greeting', 'happy', 'casual', 'joy')
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_generate_response_sad(self):
        response = self.response_generator.generate_response('comfort', 'sad', 'supportive', 'sadness')
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_generate_response_unknown_intent(self):
        response = self.response_generator.generate_response('unknown', 'neutral', 'casual', 'confused')
        self.assertEqual(response, "I'm not sure how to respond to that.")

if __name__ == '__main__':
    unittest.main()