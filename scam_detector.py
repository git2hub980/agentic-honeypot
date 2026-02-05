KEYWORDS = [
    "blocked", "verify", "urgent", "upi",
    "account", "suspended", "click",
    "otp", "bank" , "100%free", "winner" , "act now" , "guaranteed", "Don't wait", "limited time", "bonus", "gift card"
]

def progressive_confidence(message, history):
    score = 0.0
    text = message.lower()

    for kw in KEYWORDS:
        if kw in text:
            score += 0.12

    score += min(len(history)*0.03,0.3)

    return min(score, 1.0)
