import random
import time

REPLIES = {
    "en": [
        "Ok I am checking",
        "Can u wait a min?",
        "I will confirm and tell you",
        "Let me see this",
        "Give me a sec, I will do",
        "It is showing some issue",
        "I think there is a delay from bank side",
        "Something is not matching here",
        "Please wait, system is slow",
        "Ig there is something wrong",
        "OTP expired. can u resend again?",
        "Server is down right now",
        "Transaction failed. Try later",
        "Network issue detected",
        "Wait its reloading"
    ],
        "hinglish": [
        "Ek sec bhai check kar raha hoon",
        "System thoda slow hai yaar",
        "Wait karo resend karo",
        "Lagta hai bank side se delay hai",
        "OTP expire ho gaya, firse bhejo"
    ],

    "hi": [
        "Ek minute rukhiye",
        "Main dekh raha hoon",
        "Thoda samay lagega",
        "Verify ho raha hai"
    ],
    "ta": [
        "Konjam neram irukkum",
        "Naan check panren",
        "Loading aagudhu",
        "Poruthirunga"
    ],
    "te": [
        "Oka nimisham",
        "Nenu check chestunnanu",
        "Load avutundi",
        "Konchem agandi"
    ],
    "kn": [
        "Ondu nimisha",
        "Naanu check madtini",
        "Load agtide",
        "Wait maadi, nodtha iddhini"
    ],
    "ml": [
        "Oru nimisham",
        "Njan check cheyyunnu",
        "Load aakunnu",
        "Kurachu wait cheyyu"
    ],
    "mr": [
        "Ek minute thamba",
        "Mi check kartoy",
        "Load hot aahe",
        "Kripaya thoda vel"
    ],
    "gu": [
        "Ek minute raho",
        "Hu check kari rahyo chhu",
        "Load thai rahyu chhe",
        "Thodu rukoo"
    ],
    "pa": [
        "Ik minute rukoo",
        "Main check kar reha haan",
        "Load ho reha hai",
        "Thoda ruk jaoo"
    ],
    "bn": [
        "Ekto opekkha korun",
        "Ami check korchi",
        "Load hocche",
        "Doya kore wait korun"
    ],
    "or": [
        "Tikie apekhya karantu",
        "Mu check karuchi",
        "Load heuchi",
        "Daya kari rukantu"
    ],
    "ur": [
        "Ek minute rukiye",
        "Main check kar raha hoon",
        "Load ho raha hai",
        "Meherbani karke intezar karein"
    ]
}

def agent_reply(session):
    lang = session.get("language", "en")
    used = session["used_replies"]

    options = REPLIES.get(lang, REPLIES["en"])

    reply = random.choice(options)
    while reply in used:
        reply = random.choice(options)

    used.append(reply)
    session["used_replies"] = used[-11:]

    time.sleep(random.uniform(0.8, 2.5))
    return reply
