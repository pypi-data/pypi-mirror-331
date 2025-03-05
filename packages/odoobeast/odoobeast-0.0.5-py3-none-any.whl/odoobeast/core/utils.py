import re
import string
import random
from datetime import datetime
from textblob import TextBlob
import uuid
import hashlib

class Utils:
    @staticmethod
    def clean_text(text):
        """Removes special characters and extra spaces from text."""
        text = text.lower().strip()
        text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def generate_random_id(length=8):
        """Generates a random alphanumeric ID."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def generate_uuid():
        """Generates a unique UUID."""
        return str(uuid.uuid4())

    @staticmethod
    def hash_text(text):
        """Returns an SHA256 hash of the input text."""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def get_current_timestamp():
        """Returns the current timestamp in a readable format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def sentiment_analysis(text):
        """Advanced sentiment analysis using TextBlob."""
        text = Utils.clean_text(text)
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        if polarity > 0:
            return "positive"
        elif polarity < 0:
            return "negative"
        return "neutral"

    @staticmethod
    def word_count(text):
        """Counts the number of words in a text."""
        words = text.split()
        return len(words)

    @staticmethod
    def char_count(text):
        """Counts the number of characters in a text."""
        return len(text)

    @staticmethod
    def get_random_advice():
        """Returns a random piece of advice."""
        advice_list = [
            "Believe in yourself and all that you are.",
            "Stay focused and never give up.",
            "Kindness is a language everyone understands.",
            "Hard work beats talent when talent doesn’t work hard.",
            "Take breaks, but never quit.",
            "Consistency is key to long-term success.",
            "Don’t fear failure; learn from it.",
            "Embrace change and grow with it." 
        ]
        return random.choice(advice_list)

    @staticmethod
    def reverse_text(text):
        """Reverses the input text."""
        return text[::-1]

    @staticmethod
    def get_current_date():
        """Returns the current date."""
        return datetime.now().strftime("%Y-%m-%d")

# Example usage
if __name__ == "__main__":
    print("Cleaned text:", Utils.clean_text("Hello!!! How are you??"))
    print("Random ID:", Utils.generate_random_id())
    print("UUID:", Utils.generate_uuid())
    print("Hashed text:", Utils.hash_text("Odoo Beast"))
    print("Current timestamp:", Utils.get_current_timestamp())
    print("Sentiment:", Utils.sentiment_analysis("I love this project!"))
    print("Word count:", Utils.word_count("Odoo is going to be a beast AI!"))
    print("Character count:", Utils.char_count("Beast Mode"))
    print("Reversed text:", Utils.reverse_text("Beast"))
    print("Current date:", Utils.get_current_date())
    print("Random advice:", Utils.get_random_advice())
