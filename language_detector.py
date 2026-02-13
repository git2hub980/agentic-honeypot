print("ADVANCED ML-STYLE LANGUAGE DETECTOR LOADED")

import re

# -----------------------------
# Utility: Clean & tokenize text
# -----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()

# -----------------------------
# Main Detection Function
# -----------------------------
def detect_language(text: str) -> dict:
    if not text:
        return {
            "primary": "en",
            "secondary": [],
            "confidence": 0.0,
            "scores": {}
        }

    words = clean_text(text)

    # -----------------------------
    # Language Keyword Database
    # Format:
    # word: weight
    # -----------------------------
    patterns = {

        "en": {
            # normal
            "hello":1, "hi":1, "please":1, "thanks":1, "help":1,
            "money":1, "bank":1, "account":1, "update":1,

            # scam
            "otp":3, "refund":3, "verify":3, "urgent":3,
            "lottery":3, "prize":3, "winner":3,
            "investment":3, "loan":3, "credit":3,
            "debit":3, "kyc":3, "pin":3, "password":3,
            "fraud":3, "scam":3
        },

        "hi": {
            "main":1, "mera":1, "mujhe":1, "tum":1,
            "aap":1, "kya":1, "kaise":1, "haan":1,
            "nahi":1, "acha":1, "theek":1,
            "paise":1, "jaldi":1,

            "otp":3, "bank":3, "khata":3,
            "turant":3, "inaam":3,
            "lottery":3, "verify":3,
            "refund":3, "nivesh":3,
            "loan":3, "pin":3, "password":3
        },

        "hinglish": {
            "bhai":2, "yaar":2,
            "kya":1, "kyu":1, "nahi":1,
            "acha":1, "theek":1,
            "hai":1,

            "otp bhejo":3,
            "paise bhejo":3,
            "bank account":3,
            "verify karo":3,
            "click karo":3
        },

        "mr": {
            "tumhi":1, "ahe":1, "kay":1,
            "paise":1, "krupaya":1,

            "otp":3, "bank":3, "khate":3,
            "tatkal":3, "bakshis":3,
            "loan":3, "pin":3
        },

        "gu": {
            "tame":1, "che":1, "shu":1,
            "paisaa":1,

            "otp":3, "bank":3, "khatu":3,
            "turant":3, "inaam":3,
            "loan":3, "pin":3
        },

        "ta": {
            "ungal":1, "enna":1,
            "panam":1,

            "otp":3, "bank":3,
            "udane":3, "parisu":3,
            "loan":3, "password":3
        },

        "te": {
            "mee":1, "enti":1,
            "dabbulu":1,

            "otp":3, "bank":3,
            "ventane":3,
            "loan":3, "password":3
        },

        "kn": {
            "neevu":1, "enu":1,
            "hanavu":1,

            "otp":3, "bank":3,
            "takshana":3,
            "loan":3, "password":3
        },

        "ml": {
            "ningal":1, "entha":1,
            "panam":1,

            "otp":3, "bank":3,
            "udane":3,
            "loan":3, "password":3
        }
    }

    scores = {lang: 0 for lang in patterns}
    total_weight = 0

    # -----------------------------
    # Weighted Matching Logic
    # -----------------------------
    for lang, keyword_dict in patterns.items():
        for keyword, weight in keyword_dict.items():
            for word in words:
                if keyword in word:
                    scores[lang] += weight
                    total_weight += weight

    # If nothing matched
    if total_weight == 0:
        return {
            "primary": "en",
            "secondary": [],
            "confidence": 0.0,
            "scores": scores
        }

    # -----------------------------
    # Sort languages by score
    # -----------------------------
    sorted_langs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    primary_lang = sorted_langs[0][0]
    primary_score = sorted_langs[0][1]

    # Detect secondary if close score
    secondary_langs = []
    for lang, score in sorted_langs[1:]:
        if score > 0 and (primary_score - score) <= 2:
            secondary_langs.append(lang)

    confidence = round(primary_score / total_weight, 2)

    return {
        "primary": primary_lang,
        "secondary": secondary_langs,
        "confidence": confidence,
        "scores": scores
    }
