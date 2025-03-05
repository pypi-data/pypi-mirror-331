import unittest
from core.nlp import IntentClassifier

class TestIntentClassifier(unittest.TestCase):

    def setUp(self):
        self.intent_classifier = IntentClassifier()

    def test_intent_prediction(self):
        test_input = "What's the weather like today?"
        expected_intents = ["weather", "general_query"]
        predicted_intent = self.intent_classifier.predict(test_input)

        self.assertIn(predicted_intent, expected_intents)

    def test_empty_input(self):
        test_input = ""
        predicted_intent = self.intent_classifier.predict(test_input)

        self.assertEqual(predicted_intent, "unknown")

if __name__ == "__main__":
    unittest.main()
