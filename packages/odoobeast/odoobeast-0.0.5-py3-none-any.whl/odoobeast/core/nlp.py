import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC  
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

nltk.download('punkt')
nltk.download('wordnet')

# Initialize NLP tools
lemmatizer = WordNetLemmatizer()
ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')

# Expanded and advanced intent data
intent_data = [
    # Greetings
    ("Hello, how are you?", "greeting"),
    ("Hey!", "greeting"),
    ("Good morning!", "greeting"),
    ("Good night!", "farewell"),
    ("Bye, see you later!", "farewell"),

    # Assistance
    ("Can you help me with this project?", "assistance"),
    ("I’m stuck, can you guide me?", "assistance"),
    ("I need advice on something", "assistance"),

    # Weather
    ("What’s the weather like today?", "weather"),
    ("Is it going to rain tomorrow?", "weather"),
    ("How hot is it outside?", "weather"),

    # Entertainment
    ("Tell me a joke", "entertainment"),
    ("Play some music", "entertainment"),
    ("Recommend me a good movie", "entertainment"),
    ("Suggest a TV show", "entertainment"),

    # Bookings
    ("I need to book a flight", "booking"),
    ("Reserve a table at a restaurant", "booking"),
    ("Can you schedule a doctor’s appointment?", "booking"),

    # Information
    ("What’s the capital of France?", "information"),
    ("How far is the moon?", "information"),
    ("Explain quantum physics to me", "information"),

    # Personal & Emotional Support
    ("I’m feeling sad", "emotional_support"),
    ("I need someone to talk to", "emotional_support"),
    ("I’m so excited today!", "emotional_support"),
    ("I feel so lonely", "emotional_support"),
    ("I'm stressed about my exams", "emotional_support"),
    ("I’m really anxious", "emotional_support"),
    ("I feel unmotivated", "emotional_support"),
    ("I need a confidence boost", "emotional_support"),

    # Advice for Teenagers
    ("How do I deal with peer pressure?", "teen_advice"),
    ("I’m struggling with my studies", "teen_advice"),
    ("How can I manage my time better?", "teen_advice"),
    ("I need tips for self-confidence", "teen_advice"),
    ("How do I stop overthinking?", "teen_advice"),
    ("How do I make new friends?", "teen_advice"),
    ("I’m scared about my future", "teen_advice"),
    ("How can I deal with failure?", "teen_advice"),

    # Productivity
    ("Set a reminder for 5 PM", "productivity"),
    ("Create a to-do list", "productivity"),
    ("What’s on my schedule today?", "productivity"),
    ("Help me plan my week", "productivity"),
    ("Track my habits", "productivity"),

    # Jokes & Fun
    ("Make me laugh", "entertainment"),
    ("Tell me a riddle", "entertainment"),
    ("Let’s play a game", "game"),
    ("Do you know any fun facts?", "entertainment"),

    # Knowledge
    ("What’s the theory of relativity?", "information"),
    ("Who invented the telephone?", "information"),
    ("How does the internet work?", "information"),
    ("What’s the speed of light?", "information"),
    ("Explain black holes", "information")
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

# Named Entity Recognition (NER)
def extract_entities(text):
    entities = ner_pipeline(text)
    return {entity['word']: entity['entity'] for entity in entities}

if __name__ == "__main__":
    sample_text = "Hey there! I need some help with my project. Can you guide me?"
    print("Preprocessed Text:", preprocess_text(sample_text))
    print("Sentiment:", analyze_sentiment(sample_text))
    print("Entities:", extract_entities(sample_text))
    print("Intent:", detect_intent(sample_text))
