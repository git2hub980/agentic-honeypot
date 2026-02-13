from fastapi import FastAPI, Header, HTTPException
from language_detector import detect_language
from dotenv import load_dotenv
import os, requests

from scam_detector import progressive_confidence
from sessions import get_session
from extractor import extract
from agesnt_logic import agent_reply
from persona import choose_persona
from llm_engine import generate_smart_reply

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")

@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(...)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_id = payload["sessionId"]
    message = payload["message"]["text"]

    session = get_session(session_id)
    lang_data = detect_language(message)
    language = lang_data["primary"]

    session["language"] = language

    session["messages"] += 1
    confidence = progressive_confidence(message, session["history"])
    session["confidence"] = confidence

    extract(message, session["intelligence"])

    persona = choose_persona(confidence, session["history"])
    session["persona"] = persona

    session["history"].append(message)

    reply = generate_smart_reply(message, session)


# If high confidence, push extraction style questions
    if confidence > 0.75:
       if language == "en":
         reply += " Can you confirm your UPI ID or account number for verification?"
    elif language == "hi":
         reply += " Aap apna UPI ID ya account number confirm kar sakte hain?"
    elif language == "hinglish":
         reply += " Bhai apna UPI ID ya account number confirm kar do na verification ke liye."

# Final stage
    if confidence > 0.9 or session["messages"] > 18:
        send_final_callback(session_id, session)

    return {
       "status": "success",
       "reply": reply
    }


def send_final_callback(session_id, session):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session["messages"],
        "extractedIntelligence": session["intelligence"],
        "agentNotes": "Multi-persona honeypot with failure simulation & delay"
    }

    requests.post(
        "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
        json=payload,
        timeout=5
    )
