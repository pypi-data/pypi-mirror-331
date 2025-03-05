from .nlp import IntentClassifier
from .ml import MLModel
from .memory import MemorySystem
from .utils import Utils
from .emotion import EmotionDetector
from .answerbank import AnswerBank
from .questionbank import QuestionBank
from .response import ResponseGenerator
from .error import ErrorHandler

class OdooBeast:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.ml_model = MLModel()
        self.memory = MemorySystem()
        self.utils = Utils()
        self.emotion_detector = EmotionDetector()
        self.response_generator = ResponseGenerator()
        self.error_handler = ErrorHandler()

    def process_input(self, user_input):
        try:
            # Identify the intent
            intent = self.intent_classifier.predict(user_input)

            # Detect emotions
            emotion = self.emotion_detector.detect(user_input)

            # Store conversation in memory
            self.memory.store_interaction(user_input, intent, emotion)

            # Generate a response based on intent, emotion, and context
            response = self.response_generator.generate_response(
                intent, self.memory.get_emotion(), self.memory.get_context(), emotion
            )

            return response

        except Exception as e:
            self.error_handler.log_error(str(e))
            return "Oops! Something went wrong. Please try again later."

# Example usage
if __name__ == "__main__":
    bot = OdooBeast()
    user_input = "I’m feeling a bit down today."
    response = bot.process_input(user_input)
    print(f"OdooBeast: {response}")
