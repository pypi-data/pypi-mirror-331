import random

class GreetingGenerator:
    def __init__(self):
        self.greetings = [
            "Hey {}! Hope you're having an amazing day! 🚀",
            "Hello {}, ready to conquer the day? 💪",
            "Yo {}! Let's make today awesome! 🎉",
            "Hi {}! Stay positive and keep coding! 😃",
            "Good vibes only, {}! Hope you're doing great! 🌟"
        ]
        self.farewells = [
            "Goodbye {}! Keep coding and stay awesome! 😊",
            "See you later, {}! Keep rocking! 🤘",
            "Take care, {}! Until next time. ✨",
            "Bye {}! Wishing you success and happiness! 🍀",
            "Catch you soon, {}! Keep shining! 🌞"
        ]

    def greet(self, name):
        return random.choice(self.greetings).format(name)

    def goodbye(self, name):
        return random.choice(self.farewells).format(name)

greeting_generator = GreetingGenerator()

def greet(name):
    return greeting_generator.greet(name)

def goodbye(name):
    return greeting_generator.goodbye(name)