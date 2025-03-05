import unittest
from core.memory import MemorySystem

class TestMemorySystem(unittest.TestCase):

    def setUp(self):
        self.memory = MemorySystem()

    def test_store_interaction(self):
        self.memory.store_interaction("Hello", "greeting", "happy")
        history = self.memory.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['user_input'], "Hello")
        self.assertEqual(history[0]['intent'], "greeting")
        self.assertEqual(history[0]['emotion'], "happy")

    def test_get_emotion(self):
        self.memory.store_interaction("I'm sad", "feeling", "sad")
        emotion = self.memory.get_emotion()
        self.assertEqual(emotion, "sad")

    def test_get_context(self):
        self.memory.store_interaction("What's the weather?", "question", "curious")
        context = self.memory.get_context()
        self.assertEqual(context, "question")

    def test_clear_memory(self):
        self.memory.store_interaction("Hi", "greeting", "neutral")
        self.memory.clear_memory()
        history = self.memory.get_history()
        self.assertEqual(len(history), 0)

if __name__ == "__main__":
    unittest.main()
