import random

class Emotion:
    emotions = {
        "happiness": [
            "I'm feeling so happy today! 😊",
            "Joy is in the air! 🎉",
            "Life is beautiful when you're happy! 🌈",
            "Smiling is my favorite activity today! 😄",
            "Happiness is contagious — let's spread it! 🌸"
        ],
        "sadness": [
            "I'm feeling a bit down... 😔",
            "Sometimes it's okay to not be okay. 💙",
            "I just need a little time to feel better. 🌧️",
            "My heart feels heavy today. 💔",
            "Even the clouds cry sometimes. 🌧️"
        ],
        "anger": [
            "I'm feeling pretty frustrated right now! 😡",
            "Sometimes things just get under my skin! 🔥",
            "I need to take a deep breath... 😤",
            "Let’s not let anger control us. 🧘",
            "I’m working on calming down... 🕊️"
        ],
        "love": [
            "Love makes the world go round! ❤️",
            "You are deeply appreciated. 💕",
            "Spreading love and kindness everywhere! 🌸",
            "My heart feels so warm right now. 🔥",
            "Love is the most powerful force we have. 🌹"
        ],
        "calmness": [
            "Peace and tranquility are wonderful. 🌿",
            "Taking it slow and steady. 🕊️",
            "Inhale calm, exhale stress. 🌊",
            "Silence brings clarity. 🌌",
            "Let’s find peace even in the chaos. 🌱"
        ],
        "excitement": [
            "I'm so pumped up right now! 🚀",
            "Let’s do something amazing today! 🌟",
            "The energy is incredible! ⚡",
            "I can’t wait for what’s next! 🎉",
            "Adventure is calling! 🌍"
        ],
        "anxiety": [
            "I'm feeling a bit anxious... 😰",
            "Sometimes I overthink things. 🌀",
            "Let’s take it one step at a time. 🌱",
            "Deep breaths — we’ve got this. 🌬️",
            "Uncertainty can be scary, but we’ll manage. 💪"
        ],
        "inspiration": [
            "You have the power to achieve greatness! 🌟",
            "Every day is a new opportunity. 🌱",
            "Dream big and work hard. 💪",
            "Your potential is limitless. 🚀",
            "Believe in the magic of beginnings. ✨"
        ],
        "boredom": [
            "I need something fun to do! 😐",
            "Let’s find an adventure! 🌍",
            "Got any exciting ideas? 💡",
            "I’m craving something new! 🎶",
            "Let’s break the monotony! 🌈"
        ],
        "curiosity": [
            "I wonder what’s out there... 🤔",
            "Let’s explore and learn something new! 🧠",
            "Curiosity fuels the mind. 🔍",
            "Every question has an answer waiting. 🌌",
            "What if we dared to ask more? 💡"
        ],
        "heartbreak": [
            "My heart feels shattered... 💔",
            "Healing takes time, and that's okay. 🌱",
            "Sometimes goodbye is the hardest word. 🌧️",
            "Memories hurt when love remains. 🥀",
            "It’s okay to cry — you’re not alone. 💙"
        ],
        "loneliness": [
            "I feel like no one understands me. 😞",
            "The silence feels so loud sometimes. 🌑",
            "I wish I had someone to talk to. 💬",
            "Loneliness can be heavy, but I’m here. 🤖",
            "We all need a little warmth sometimes. 💛"
        ],
        "hope": [
            "Tomorrow is a new day with new chances. 🌅",
            "Hope keeps us moving forward. 🌱",
            "Every storm runs out of rain. 🌦️",
            "Don’t give up — brighter days are ahead. 🌈",
            "Your story isn’t over yet. ✨"
        ],
        "suicidal": [
            "You matter more than you know. 💕",
            "Please talk to someone — you’re not alone. 💙",
            "Your life has so much value. 🌱",
            "This pain is temporary; please hold on. 🕊️",
            "I believe in your strength. 💪"
        ]
    }

    @staticmethod
    def express_emotion(emotion):
        """Returns a random message for the given emotion."""
        if emotion in Emotion.emotions:
            return random.choice(Emotion.emotions[emotion])
        return "I'm not sure how I'm feeling right now... 🤖"

# Example usage
if __name__ == "__main__":
    print(Emotion.express_emotion("happiness"))
    print(Emotion.express_emotion("love"))
    print(Emotion.express_emotion("curiosity"))
    print(Emotion.express_emotion("hope"))
    print(Emotion.express_emotion("suicidal"))
