import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

nltk.download('punkt')
nltk.download('wordnet')

# Initialize NLP tools
lemmatizer = WordNetLemmatizer()

# Expanded and advanced intent data
intent_data = [
    ("Hello, how are you?", "greeting"),
    ("Hey!", "greeting"),
    ("Good morning!", "greeting"),
    ("Good night!", "farewell"),
    ("Bye, see you later!", "farewell"),
    ("Can you help me with this project?", "assistance"),
    ("I’m stuck, can you guide me?", "assistance"),
    ("I need advice on something", "assistance"),
    ("What’s the weather like today?", "weather"),
    ("Is it going to rain tomorrow?", "weather"),
    ("How hot is it outside?", "weather"),
    ("Tell me a joke", "entertainment"),
    ("Play some music", "entertainment"),
    ("Recommend me a good movie", "entertainment"),
    ("Suggest a TV show", "entertainment"),
    ("I need to book a flight", "booking"),
    ("Reserve a table at a restaurant", "booking"),
    ("Can you schedule a doctor’s appointment?", "booking"),
    ("What’s the capital of France?", "information"),
    ("How far is the moon?", "information"),
    ("Explain quantum physics to me", "information"),
    ("I’m feeling sad", "emotional_support"),
    ("I need someone to talk to", "emotional_support"),
    ("I’m so excited today!", "emotional_support"),
    ("I feel so lonely", "emotional_support"),
    ("I'm stressed about my exams", "emotional_support"),
    ("I’m really anxious", "emotional_support"),
    ("I feel unmotivated", "emotional_support"),
    ("I need a confidence boost", "emotional_support"),
]

# Preparing data
texts, labels = zip(*intent_data)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = np.array(labels)

# Splitting data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Training intent classifier
classifier = SVC(kernel='linear', probability=True)
classifier.fit(X_train, y_train)

# Evaluating classifier
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))

# Advanced intent detection
def detect_intent(text):
    X_input = vectorizer.transform([text])
    return classifier.predict(X_input)[0]

# Text preprocessing
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
    return lemmatized

# Sentiment analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return 'positive'
    elif sentiment < 0:
        return 'negative'
    else:
        return 'neutral'

# Conversation Memory System
class ConversationMemory:
    def __init__(self):
        self.session_memory = []
        self.long_term_memory = {}
        self.emotion_state = 'neutral'
        self.context_stack = []

    def add_to_memory(self, user_input, response, intent):
        sentiment = analyze_sentiment(user_input)
        self.emotion_state = sentiment
        memory_entry = {
            'user_input': user_input,
            'response': response,
            'intent': intent,
            'sentiment': sentiment
        }
        self.session_memory.append(memory_entry)
        self.context_stack.append(memory_entry)
        if len(self.context_stack) > 5:
            self.context_stack.pop(0)
        self.prioritize_memory(intent, memory_entry)

    def prioritize_memory(self, intent, memory_entry):
        if intent not in self.long_term_memory:
            self.long_term_memory[intent] = []
        self.long_term_memory[intent].append(memory_entry)
        self.long_term_memory[intent] = self.long_term_memory[intent][-5:]

    def get_context(self, num_turns=3):
        return self.context_stack[-num_turns:]

    def get_emotion(self):
        return self.emotion_state

    def adapt_response(self, response):
        if self.emotion_state == 'positive':
            return f"😊 {response}"
        elif self.emotion_state == 'negative':
            return f"😔 {response}"
        else:
            return response

memory = ConversationMemory()

if __name__ == "__main__":
    sample_text = "Hey there! I need some help with my project. Can you guide me?"
    intent = detect_intent(sample_text)
    response = "Sure, I’d be happy to help!"
    memory.add_to_memory(sample_text, response, intent)
    adapted_response = memory.adapt_response(response)
    print("Session Memory:", memory.get_context())
    print("Current Emotion State:", memory.get_emotion())
    print("Adapted Response:", adapted_response)
