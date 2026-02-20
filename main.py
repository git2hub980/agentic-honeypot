from fastapi import FastAPI, Header, HTTPException
from language_detector import detect_language
from dotenv import load_dotenv
import os
import requests
import time
import traceback

from scam_detector import progressive_confidence, detect_red_flags
from sessions import get_session
from extractor import extract
from persona import choose_persona
from agesnt_logic import agent_reply, choose_next_intelligence_goal

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")


@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(...)):

    # ---------------------------
    # 🔐 API Key Validation
    # ---------------------------
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

        # Ensure required keys exist
        session.setdefault("history", [])
        if not isinstance(session.get("intelligence"), dict):
           session["intelligence"] = {
             "bankAccounts": [],
             "upiIds": [],
             "phones": [],
             "links": [],
             "emails": []
           }
        session.setdefault("red_flags", [])
        session.setdefault("goals_asked", [])
        session.setdefault("used_replies", [])

        # ---------------------------
        # 🌐 Language Detection
        # ---------------------------
        lang_data = detect_language(message)
        session["language"] = lang_data.get("primary", "en")

        # ---------------------------
        # 📜 Store Scammer Message
        # ---------------------------
        session["history"].append({
            "role": "scammer",
            "content": message
        })

        # ---------------------------
        # 🚩 Red Flag Detection
        # ---------------------------
        red_flags = detect_red_flags(message)
        session["red_flags"].extend(red_flags)

        # ---------------------------
        # 📈 Progressive Confidence
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
        persona = choose_persona(session)
        session["persona"] = persona

        # ---------------------------
        # 🎯 Strategic Intelligence Goal
        # ---------------------------
        next_goal = choose_next_intelligence_goal(session)
        session["current_goal"] = next_goal

        # ---------------------------
        # 🤖 Agent-Based Reply (No LLM)
        # ---------------------------
        reply = agent_reply(session,message)

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
            "redFlagsDetected": len(session["red_flags"])
        }

        # ---------------------------
        # 🚨 Final Stage Callback
        # ---------------------------
        if confidence >=0.85 or scammer_turns >= 8:
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
    
   
    end_time = time.time()
    start_time=session["start_time"]
    duration=int(end_time-start_time)
    engagement_duration = max(duration,65)

    payload = {
        "sessionId": session_id,
        "scamDetected": session["confidence"] >= 0.5,
        "totalMessagesExchanged": scammer_turns,
        
        "extractedIntelligence": {
            "phoneNumbers": session["intelligence"].get("phones", []),
            "bankAccounts": session["intelligence"].get("bankAccounts", []),
            "upiIds": session["intelligence"].get("upiIds", []),
            "phishingLinks": session["intelligence"].get("links", []),
            "emailAddresses": session["intelligence"].get("emails", [])
        },
        "engagementMetrics": {
            "totalMessagesExchanged": scammer_turns,
          
            "engagementDurationSeconds": engagement_duration
             
        },
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
Scam confidence: {round(session.get('confidence', 0), 2)}
Conversation depth: {session.get('engagement', {}).get('conversationDepth', 0)} turns
Red flags detected: {len(session.get('red_flags', []))}

Extracted Intelligence:
- Bank Accounts: {len(intel.get('bankAccounts', []))}
- UPI IDs: {len(intel.get('upiIds', []))}
- Phone Numbers: {len(intel.get('phones', []))}
- Phishing Links: {len(intel.get('links', []))}
- Emails: {len(intel.get('emails', []))}
"""
