def detect_language(text: str) -> str:
    text = text.lower()

    patterns = {
        "hinglish": ["bhai", "yaar", "kya", "kyu", "nahi", "acha", "theek", "hai na", "arrey"],
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

    def detect_language(text: str) -> str:
        text = text.lower()

    patterns = {
        ...
    }

    scores = {lang: 0 for lang in patterns}

    for lang, keywords in patterns.items():
        for word in keywords:
            if word in text:
                scores[lang] += 1

    best_lang = max(scores, key=scores.get)

    if scores[best_lang] == 0:
        return "en"

    return best_lang
