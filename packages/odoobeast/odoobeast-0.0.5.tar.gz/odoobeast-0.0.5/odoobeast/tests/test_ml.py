import unittest
from core.ml import MLModel

class TestMLModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = MLModel()

    def test_train_model(self):
        training_data = [
            ("Hello, how are you?", "greeting"),
            ("What’s the weather like?", "weather")
        ]
        result = self.model.train(training_data)
        self.assertTrue(result)

    def test_predict(self):
        input_text = "Hello!"
        prediction = self.model.predict(input_text)
        self.assertIsInstance(prediction, str)

    def test_predict_untrained_model(self):
        model = MLModel()
        input_text = "Hello!"
        with self.assertRaises(RuntimeError):
            model.predict(input_text)

if __name__ == "__main__":
    unittest.main()
