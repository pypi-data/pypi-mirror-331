from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

class PrebuiltModels:
    def __init__(self):
        self.intent_model = self._load_intent_model()
        self.emotion_model = self._load_emotion_model()

    def _load_intent_model(self):
        try:
            model = joblib.load('models/intent_model.pkl')
            return model
        except FileNotFoundError:
            return self._train_default_intent_model()

    def _load_emotion_model(self):
        try:
            model = joblib.load('models/emotion_model.pkl')
            return model
        except FileNotFoundError:
            return self._train_default_emotion_model()

    def _train_default_intent_model(self):
        # Placeholder training data
        training_data = ["hello", "how are you", "what’s up"]
        labels = ["greeting", "greeting", "casual"]

        pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('classifier', MultinomialNB())
        ])

        pipeline.fit(training_data, labels)
        joblib.dump(pipeline, 'models/intent_model.pkl')
        return pipeline

    def _train_default_emotion_model(self):
        # Placeholder training data
        training_data = ["I’m happy", "I’m sad", "I’m angry"]
        labels = ["happy", "sad", "angry"]

        pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('classifier', MultinomialNB())
        ])

        pipeline.fit(training_data, labels)
        joblib.dump(pipeline, 'models/emotion_model.pkl')
        return pipeline

    def predict_intent(self, text):
        return self.intent_model.predict([text])[0]

    def predict_emotion(self, text):
        return self.emotion_model.predict([text])[0]
