
import random
import time

REPLIES = {
    "normal": [
        "Okay I am checking",
        "Can you wait a min?",
        "I will confirm and tell you",
        "Let me  this",
        "Give me a sec, I will do"
    ],
    "suspicious": [
        "It is showing some issue.",
        "I think there is a delay from bank side.",
        "Something is not matching here.",
        "Please wait, system is slow."
        "I guess there is something wrong."
    ],
    "failure": [
        "OTP expired. Please resend.",
        "Server is down right now.",
        "Transaction failed. Try later.",
        "Network issue detected."
        "Wait its reloading."
    ]
}

def agent_reply(session):
    persona = session["persona"]
    used = session["used_replies"]

    options = [r for r in REPLIES[persona] if r not in used]
    if not options:
        options = REPLIES[persona]

    reply = random.choice(options)

    used.append(reply)
    session["used_replies"] = used[-5:]  # cap to last 5

    # Human delay
    time.sleep(random.uniform(0.5, 1.8))

    return reply
