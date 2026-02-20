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

    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:

        session_id = payload.get("sessionId")
        message = payload.get("message", {}).get("text")

        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Invalid payload format")

        session = get_session(session_id)
        if "start_time" not in session:
            session["start_time"] = time.time()

        session.setdefault("history", [])
        session.setdefault("agent_notes", [])
        if not isinstance(session.get("intelligence"), dict):
           session["intelligence"] = {
             "bankAccounts": [],
             "upiIds": [],
             "phones": [],
             "links": [],
             "emails": [],
             "otpCodes": [],
             "ifscCodes":[]
           }
        session.setdefault("red_flags", [])
        session.setdefault("goals_asked", [])
        session.setdefault("used_replies", [])

        lang_data = detect_language(message)
        session["language"] = lang_data.get("primary", "en")

        session["history"].append({
            "role": "scammer",
            "content": message
        })

        red_flags = detect_red_flags(message)
        session["red_flags"].extend(red_flags)

        confidence = progressive_confidence(message, session["history"])
        session["confidence"] = confidence

        extract(message, session["intelligence"])

        persona = choose_persona(session)
        session["persona"] = persona

        next_goal = choose_next_intelligence_goal(session)
        session["current_goal"] = next_goal

        reply = agent_reply(session,message)

        session["history"].append({
            "role": "honeypot",
            "content": reply
        })

        scammer_turns = len(
            [m for m in session["history"] if m["role"] == "scammer"]
        )

        session["engagement"] = {
            "conversationDepth": scammer_turns,
            "confidenceScore": confidence,
            "personaUsed": persona,
            "redFlagsDetected": len(session["red_flags"])
        }

        
        send_final_callback(session_id, session)

        return {
            "status": "success",
            "reply": reply,
            "confidence": confidence
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


def send_final_callback(session_id, session):
    # Force extraction from full conversation
    for msg in session["history"]:
      if msg["role"] == "scammer":
         extract(msg["content"], session["intelligence"])

    scammer_turns = len(
        [m for m in session["history"] if m["role"] == "scammer"]
    )
    
    end_time = time.time()
    start_time = session.get("start_time")
    duration = int(end_time - start_time) if start_time else 0
    engagement_duration = max(duration, 60)

    payload = {
        "sessionId": session_id,
        "scamDetected": session["confidence"] >= 0.5,
        "totalMessagesExchanged": scammer_turns,
        
        "extractedIntelligence": {
            "phoneNumbers": session["intelligence"].get("phones", []),
            "bankAccounts": session["intelligence"].get("bankAccounts", []),
            "upiIds": session["intelligence"].get("upiIds", []),
            "phishingLinks": session["intelligence"].get("links", []),
            "emailAddresses": session["intelligence"].get("emails", []),
            "otpCodes": session["intelligence"].get("otpCodes", []),
            "ifscCodes": session["intelligence"].get("ifscCodes", [])
        },
        "engagementMetrics": {
            "totalMessagesExchanged": scammer_turns,
            "engagementDurationSeconds": engagement_duration
        },
        "redFlags": session.get("red_flags", []),
        "agentNotes": generate_agent_notes(session)
    }

    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
        print("Callback status:", response.status_code)
        print("Callback response:", response.text)
    except Exception as e:
        print("Callback error:", str(e))


def generate_agent_notes(session):

    intel = session["intelligence"]

    return {
        "scamConfidence": round(session.get("confidence", 0), 2),
        "conversationDepth": session.get("engagement", {}).get("conversationDepth", 0),
        "redFlagsDetected": len(session.get("red_flags", [])),
        "extractedCounts": {
            "bankAccounts": len(intel.get("bankAccounts", [])),
            "upiIds": len(intel.get("upiIds", [])),
            "phoneNumbers": len(intel.get("phones", [])),
            "phishingLinks": len(intel.get("links", [])),
            "emails": len(intel.get("emails", [])),
            "otpCodes": len(intel.get("otpCodes", [])),
            "ifscCodes": len(intel.get("ifscCodes", []))
        }
    }
