
import unittest
from core.nlp import IntentClassifier

class TestIntentClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = IntentClassifier()

    def test_predict_intent(self):
        user_input = "How's the weather today?"
        intent = self.classifier.predict(user_input)
        self.assertIsInstance(intent, str)
        self.assertIn(intent, ["greeting", "weather", "farewell", "unknown"])

    def test_empty_input(self):
        user_input = ""
        intent = self.classifier.predict(user_input)
        self.assertEqual(intent, "unknown")

    def test_unrecognized_input(self):
        user_input = "asdjkhaskjdhaksd"
        intent = self.classifier.predict(user_input)
        self.assertEqual(intent, "unknown")

if __name__ == "__main__":
    unittest.main()