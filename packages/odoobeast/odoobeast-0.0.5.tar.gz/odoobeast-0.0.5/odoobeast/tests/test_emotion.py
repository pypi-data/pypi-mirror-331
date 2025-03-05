import unittest
from core.emotion import EmotionDetector

class TestEmotionDetector(unittest.TestCase):

    def setUp(self):
        self.emotion_detector = EmotionDetector()

    def test_detect_happy_emotion(self):
        user_input = "I’m feeling so happy and excited today!"
        result = self.emotion_detector.detect(user_input)
        self.assertEqual(result, 'happy')

    def test_detect_sad_emotion(self):
        user_input = "I’m feeling really down and sad."
        result = self.emotion_detector.detect(user_input)
        self.assertEqual(result, 'sad')

    def test_detect_angry_emotion(self):
        user_input = "I’m so angry and frustrated right now!"
        result = self.emotion_detector.detect(user_input)
        self.assertEqual(result, 'angry')

    def test_detect_neutral_emotion(self):
        user_input = "It’s just a normal day, nothing special."
        result = self.emotion_detector.detect(user_input)
        self.assertEqual(result, 'neutral')

if __name__ == '__main__':
    unittest.main()