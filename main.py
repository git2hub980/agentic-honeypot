from fastapi import FastAPI, Header, HTTPException
from language_detector import detect_language
from dotenv import load_dotenv
import os
import requests
import traceback

from scam_detector import progressive_confidence, detect_red_flags
from sessions import get_session
from extractor import extract
from persona import choose_persona
from llm_engine import generate_smart_reply
from agesnt_logic import choose_next_intelligence_goal
from agesnt_logic import agent_reply

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")


@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(...)):

    # 🔐 API Key Validation
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # ---------------------------
        # 📩 Safe Payload Extraction
        # ---------------------------
        session_id = payload.get("sessionId")
        message = payload.get("message", {}).get("text")

        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Invalid payload format")

        # ---------------------------
        # 🧠 Get/Create Session
        # ---------------------------
        session = get_session(session_id)

        if "history" not in session:
            session["history"] = []

        if "intelligence" not in session:
            session["intelligence"] = {
                "bankAccounts": [],
                "upiIds": [],
                "phones": [],
                "links": [],
                "emails": []
            }

        if "goals_asked" not in session:
            session["goals_asked"] = []

        # ---------------------------
        # 🌐 Language Detection
        # ---------------------------
        lang_data = detect_language(message)
        language = lang_data.get("primary", "en")
        session["language"] = language

        # ---------------------------
        # 📜 Store Scammer Message
        # ---------------------------
        session["history"].append({
            "role": "scammer",
            "content": message
        })

        # ---------------------------
        # 🧠 Red Flag Detection
        # ---------------------------
        red_flags = detect_red_flags(message)
        session.setdefault("red_flags", []).extend(red_flags)

        # ---------------------------
        # 📈 Confidence Scoring
        # ---------------------------
        confidence = progressive_confidence(message, session["history"])
        session["confidence"] = confidence

        # ---------------------------
        # 🕵️ Intelligence Extraction
        # ---------------------------
        extract(message, session["intelligence"])

        # ---------------------------
        # 🎭 Persona Selection
        # ---------------------------
        persona = choose_persona(confidence, session["history"])
        session["persona"] = persona

        # ---------------------------
        # 🎯 Strategic Intelligence Goal
        # ---------------------------
        next_goal = choose_next_intelligence_goal(session)
        session["current_goal"] = next_goal

        # ---------------------------
        # 🤖 Generate Smart Reply
        # ---------------------------
        reply = agent_reply(session, message)

        # ---------------------------
        # 📜 Store Honeypot Reply
        # ---------------------------
        session["history"].append({
            "role": "honeypot",
            "content": reply
        })

        # ---------------------------
        # 📊 Engagement Metrics
        # ---------------------------
        scammer_turns = len(
            [m for m in session["history"] if m["role"] == "scammer"]
        )

        session["engagement"] = {
            "conversationDepth": scammer_turns,
            "confidenceScore": confidence,
            "personaUsed": persona,
            "redFlagsDetected": len(session.get("red_flags", []))
        }

        # ---------------------------
        # 🚨 Final Stage Callback
        # ---------------------------
        if confidence > 0.85 or scammer_turns >= 8:
            send_final_callback(session_id, session)

        return {
            "status": "success",
            "reply": reply,
            "confidence": confidence
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


# --------------------------------------------------
# 🚨 Final Callback (Judge-Focused Payload)
# --------------------------------------------------

def send_final_callback(session_id, session):

    scammer_turns = len(
        [m for m in session["history"] if m["role"] == "scammer"]
    )

    payload = {
        "sessionId": session_id,
        "scamDetected": session["confidence"] > 0.7,
        "totalMessagesExchanged": scammer_turns,
        "engagementMetrics": session.get("engagement", {}),
        "extractedIntelligence": session["intelligence"],
        "redFlags": session.get("red_flags", []),
        "agentNotes": generate_agent_notes(session)
    }

    try:
        requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
    except:
        pass


def generate_agent_notes(session):

    intel = session["intelligence"]

    return f"""
Scam confidence: {round(session['confidence'],2)}
Conversation depth: {session['engagement']['conversationDepth']} turns
Red flags detected: {len(session.get('red_flags', []))}

Extracted Intelligence:
- Bank Accounts: {len(intel['bankAccounts'])}
- UPI IDs: {len(intel['upiIds'])}
- Phone Numbers: {len(intel['phones'])}
- Phishing Links: {len(intel['links'])}
- Emails: {len(intel['emails'])}
"""
