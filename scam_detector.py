SCAM_KEYWORDS = [
    "blocked", "verify", "urgent", "upi",
    "account", "suspended", "click",
    "otp", "bank" , "100%free", "winner" , "act now" , "guaranteed", "Don't wait", "limited time", "bonus", "gift card"
]

def progressive_confidence(text, history):
    score = 0.0
    text = text.lower()

    for kw in SCAM_KEYWORDS:
        if kw in text:
            score += 0.12

    score += 0.08 * len(history)

    return min(score, 1.0)
