print("ADVANCED LANGUAGE DETECTOR LOADED")

import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # remove punctuation
    return text.split()

def detect_language(text: str) -> str:
    if not text:
        return "en"

    words = clean_text(text)

    patterns = {

        # ---------------- ENGLISH ----------------
        "en": [
            # normal
            "hello","hi","please","thanks","thank","yes","no","what","why","how",
            "when","where","problem","help","money","bank","account","otp",
            "link","click","update","verify","confirm","details","urgent",
            "offer","reward","win","lottery","gift","call","message","email",

            # scam related
            "refund","transaction","blocked","suspended","security","alert",
            "free","bonus","limited","prize","winner","congratulations",
            "claim","investment","profit","guarantee","loan","credit","debit",
            "kyc","atm","password","pin","fraud","scam","risk"
        ],

        # ---------------- HINDI ----------------
        "hi": [
            # normal
            "main","mera","meri","mujhe","tum","aap","kya","kyun","kaise",
            "haan","nahi","acha","theek","ghar","paise","kaam","jaldi",
            "kripya","dhanyavaad","samajh","bolo","batao","hai","tha",

            # scam
            "otp","bank","khata","account","turant","inaam","jeet",
            "lottery","free","link","verify","jankari","update",
            "suraksha","transaction","refund","call","message",
            "nivesh","loan","credit","debit","pin","password"
        ],

        # ---------------- HINGLISH ----------------
        "hinglish": [
            "bhai","yaar","kya","kyu","nahi","acha","theek","hai na",
            "arrey","jaldi karo","paise bhejo","otp bhejo","bank account",
            "free gift","click karo","verify karo","update karo"
        ],

        # ---------------- MARATHI ----------------
        "mr": [
            "tumhi","ahe","kay","ka","kasa","paise","krupaya",
            "lagel","bank","khate","otp","tatkal","bakshis",
            "jinkla","link","tapasa","sudharna","paratava",
            "nivesh","karja","pin","password"
        ],

        # ---------------- GUJARATI ----------------
        "gu": [
            "tame","che","shu","kem","paisaa","krupaya",
            "bank","khatu","otp","turant","inaam","jeeto",
            "link","check","sudharo","refund","rokad",
            "nivesh","loan","pin","password"
        ],

        # ---------------- TAMIL ----------------
        "ta": [
            "ungal","irukku","enna","eppadi","panam","dayavu",
            "bank","kanakku","otp","udane","parisu","vangi",
            "link","saripaar","update","thiruppi","mudhal",
            "loan","kadandhu","password","pin"
        ],

        # ---------------- TELUGU ----------------
        "te": [
            "mee","undi","enti","ela","dabbulu","dayachesi",
            "bank","khata","otp","ventane","bahumathi",
            "gelicharu","link","dhruvikarinchu","update",
            "refund","nivesham","appu","pin","password"
        ],

        # ---------------- KANNADA ----------------
        "kn": [
            "neevu","iddira","enu","hege","hanavu","dayavittu",
            "bank","khate","otp","takshana","bahumana",
            "geluvu","link","parishi","update",
            "marali","hogu","sala","pin","password"
        ],

        # ---------------- MALAYALAM ----------------
        "ml": [
            "ningal","undu","entha","engane","panam","dayavaayi",
            "bank","account","otp","udane","sammanam",
            "jayichu","link","shari","update",
            "refund","nikshepam","loan","pin","password"
        ]
    }

    scores = {lang: 0 for lang in patterns}

    for lang, keywords in patterns.items():
        for word in keywords:
            for user_word in words:
                if word in user_word:
                    scores[lang] += 1

    best_lang = max(scores, key=scores.get)

    if scores[best_lang] == 0:
        return "en"

    return best_lang
