import random

EARLY_STAGE = [
    "Okay, doing that now.",
    "One moment, I'm checking.",
    "Alright, proceeding as you said."
]

MID_STAGE = [
    "It's loading, please wait.",
    "Almost done, just a second.",
    "It’s asking me to confirm something."
]

LATE_STAGE = [
    "It says verification failed once.",
    "Hmm, it's showing an error.",
    "Let me ask my nephew, he understands this better."
]

NEPHEW_STAGE = [
    "Hi, he asked me to help. What exactly should I do?",
    "Which app should I open for this?",
    "Can you resend the details once more?"
]

def agent_reply(confidence, persona, message_count):
    # EARLY conversation
    if message_count < 5:
        return random.choice(EARLY_STAGE)

    # MID conversation
    if message_count < 10:
        return random.choice(MID_STAGE)

    # Switch persona
    if persona == "nephew":
        return random.choice(NEPHEW_STAGE)

    # FINAL delay stage
    return random.choice(LATE_STAGE)
