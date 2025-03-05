import random

class QuestionBank:
    questions = {
        "what": [
            "What is the meaning of life?",
            "What are you doing right now?",
            "What makes you happy?",
            "What’s your favorite thing to talk about?",
            "What do you think about the future?"
        ],
        "where": [
            "Where are you from?",
            "Where can I find peace of mind?",
            "Where do dreams take us?",
            "Where should I go when I feel lost?",
            "Where do we find true happiness?"
        ],
        "who": [
            "Who inspires you the most?",
            "Who do you trust when things get tough?",
            "Who do you want to become?",
            "Who understands you the best?",
            "Who’s your closest friend?"
        ],
        "how": [
            "How can I stay motivated?",
            "How do I handle failure?",
            "How can I become a better person?",
            "How do you know when you’re on the right path?",
            "How can I make a difference in the world?"
        ],
        "when": [
            "When do you feel most alive?",
            "When is the right time to take a risk?",
            "When should I let go of the past?",
            "When do you know you’ve found your purpose?",
            "When is the best time to start something new?"
        ],
        "why": [
            "Why do we chase our dreams?",
            "Why is kindness so important?",
            "Why do we fear failure?",
            "Why do we need love in our lives?",
            "Why does hope keep us going?"
        ]
    }

    @staticmethod
    def get_random_question(type):
        """Returns a random question from the specified type."""
        if type in QuestionBank.questions:
            return random.choice(QuestionBank.questions[type])
        return "I’m not sure what to ask right now... 🤔"

# Example usage
if __name__ == "__main__":
    print(QuestionBank.get_random_question("what"))
    print(QuestionBank.get_random_question("where"))
    print(QuestionBank.get_random_question("who"))
    print(QuestionBank.get_random_question("how"))
    print(QuestionBank.get_random_question("when"))
    print(QuestionBank.get_random_question("why"))
