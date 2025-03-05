import random
class AnswerBank:
    answers = {
        "yes": [
            "Absolutely! 🌟",
            "Yes, without a doubt! 💯",
            "Definitely, no question about it! 💪",
            "For sure! 😊",
            "Yes, and I’m excited about it! 🚀"
        ],
        "no": [
            "Not this time. 💔",
            "Nope, sorry! 😕",
            "I don’t think so. 🤔",
            "Nah, not really. 😅",
            "No way! 🙅‍♂️"
        ],
        "maybe": [
            "Could be! 🤷‍♂️",
            "It’s possible. 🌱",
            "Not sure, but let’s find out! 🔍",
            "That’s a big maybe! 🌈",
            "50-50 on this one! ⚖️"
        ],
        "hmm": [
            "I’m thinking... 🤔",
            "Interesting question! 🧠",
            "Let’s ponder that a bit. 🌌",
            "Hmm, I wonder too! 🤷‍♀️",
            "Deep thoughts incoming... 💭"
        ],
        "hey": [
            "Hey there! 👋",
            "What’s up? 😊",
            "Yo! How’s it going? 💬",
            "Hello, my friend! 💕",
            "Hey! Ready to chat? 🚀"
        ],
        "yeah": [
            "Yeah, totally! 🎉",
            "Exactly! 💯",
            "Couldn’t agree more! 👍",
            "For sure! 😊",
            "That’s right! 🌟"
        ],
        "breakup": [
            "I’m so sorry you’re feeling this way. 💔 I’m here for you.",
            "It hurts now, but time heals. You’re stronger than you know. 🌱",
            "Let’s take this one step at a time. You deserve peace. 🌸",
            "Sometimes letting go opens the door to better things. 🌈",
            "I believe in your strength. You’ll get through this. 💪"
        ],
        "suicidal": [
            "I’m really sorry you feel this way. Please talk to someone you trust. ❤️",
            "You’re not alone. Reach out to a friend, family member, or counselor. 🌸",
            "Your life matters. Please seek support from professionals. 💕",
            "Stay with us — your story isn’t over yet. 🌈",
            "You are loved, and you deserve help and care. 💖"
        ],
        "comfort": [
            "It’s okay to feel this way. Take a deep breath. 🌱",
            "I’m here for you — no matter what. 💕",
            "You’re stronger than you think. I believe in you. 💪",
            "It’s okay to take a break. Rest and recharge. 🌸",
            "You’re doing your best, and that’s enough. 🌟"
        ]
    }

    @staticmethod
    def get_random_answer(response_type):
        if response_type in AnswerBank.answers:
            return random.choice(AnswerBank.answers[response_type])
        return "I’m not sure about that yet... But I’m learning! 💡"

# Example usage
if __name__ == "__main__":
    response_type = "yeah"
    answer = AnswerBank.get_random_answer(response_type)
    print(f"A: {answer}")
