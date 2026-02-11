from fastapi import FastAPI, Header, HTTPException
from language_detector import detect_language
from dotenv import load_dotenv
import os, requests

from scam_detector import progressive_confidence
from sessions import get_session
from extractor import extract
from agesnt_logic import agent_reply
from persona import choose_persona
from rag_engine import get_rag_reply


load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")

@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session_id = payload["sessionId"]
    message = payload["message"]["text"]

    session = get_session(session_id)
    lang = detect_language(message)
    session["language"] = lang

    session["messages"] += 1
    confidence = progressive_confidence(message, session["history"])
    session["confidence"] = confidence

    extract(message, session["intelligence"])

    persona = choose_persona(confidence, session["history"])
    session["persona"] = persona

    session["history"].append(message)

    # Get intelligent reply from dataset
    rag_reply = get_rag_reply(message, lang)

# If dataset doesn't match, fallback to human delay style
    if rag_reply == "Please wait...":
      reply = agent_reply(session)
    else:
      reply = rag_reply

# If high confidence, push extraction style questions
    if confidence > 0.75:
      if lang == "en":
        reply += " Can you confirm your UPI ID or account number for verification?"
    elif lang == "hi":
        reply += " Aap apna UPI ID ya account number confirm kar sakte hain?"
    elif lang == "hinglish":
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
