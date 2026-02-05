from fastapi import FastAPI, Header, HTTPException
from language_detector import detect_language
from dotenv import load_dotenv
import os, requests

from scam_detector import progressive_confidence
from sessions import get_session
from extractor import extract
from agesnt_logic import agent_reply
from persona import choose_persona

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

    if confidence > 0.9 or session["messages"] > 18:
        send_final_callback(session_id, session)
        return {
            "status": "success",
            "reply": agent_reply(session)
        }

    return {
        "status": "success",
        "reply": agent_reply(session)
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
