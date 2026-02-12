KEYWORDS = {
    "otp": 0.25,
    "verify": 0.2,
    "urgent": 0.2,
    "blocked": 0.2,
    "suspended": 0.2,
    "bank": 0.15,
    "account": 0.1,
    "click": 0.15,
    "upi": 0.2,
    "winner": 0.2,
    "transfer": 0.2,
    "payment": 0.2,
    "processing fee": 0.25,
    "beneficiary": 0.25,
    "refund": 0.2,
    "security code": 0.3,
    "act now": 0.2,
    "guaranteed": 0.15,
    "don't wait": 0.2,
    "limited time": 0.2,
    "bonus": 0.15,
    "gift card": 0.25
}

def progressive_confidence(message, history):
    score = 0.0
    text = message.lower()

    for kw, weight in KEYWORDS.items():
        if kw in text:
            score += weight

    # Conversation escalation effect
    score += min(len(history) * 0.02, 0.2)

    return min(score, 1.0)
