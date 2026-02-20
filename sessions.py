import time
SESSIONS = {}

def get_session(session_id):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "history": [],
            "confidence": 0.0,
            "messages": 0,
            "persona": {},
            "used_replies": [],
            "language": "en",
            "intelligence": 0,
            "start_time":time.time()

            # 🔥 NEW FIELDS
            "engagement_score": 0,
            "response_times": [],
            "risk_flags": [],
            "agent_notes": [],
            "scam_signals": []
        }
    return SESSIONS[session_id]
