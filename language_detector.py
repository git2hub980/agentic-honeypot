def detect_language(text: str) -> str:
    text = text.lower()

    patterns = {
        "hi": ["hai", "aap", "paise", "kripya", "turant", "jaldi"],
        "ta": ["ungal", "irukku", "panam", "udane", "konjam"],
        "te": ["mee", "undi", "dabbulu", "ventane", "konchem"],
        "kn": ["neevu", "iddira", "hanavu", "dayavittu"],
        "ml": ["ningal", "undu", "panam", "udane"],
        "mr": ["tumhi", "ahe", "paise", "krupaya"],
        "gu": ["tame", "che", "paise", "krupaya"],
        "pa": ["tusi", "hai", "paise", "jaldi"],
        "bn": ["apni", "ache", "taka", "taratari"],
        "or": ["apan", "achhi", "tanka", "sighra"],
        "ur": ["aap", "hai", "paise", "jaldi"]
    }

    for lang, keywords in patterns.items():
        if any(word in text for word in keywords):
            return lang

    return "en"
