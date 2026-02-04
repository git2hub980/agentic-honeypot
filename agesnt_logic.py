RESPONSES = [
    "Okay, doing that now.",
    "One moment.",
    "Almost done, it’s loading.",
    "Just one more step, right?",
    "It’s asking me to confirm."
]

def agent_reply():
    import random
    return random.choice(RESPONSES)
