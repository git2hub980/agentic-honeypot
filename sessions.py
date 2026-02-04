SESSIONS = {}

def get_session(session_id):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "history": [],
            "confidence": 0.0,
            "messages": 0,
            "intelligence": {
                "upiIds": [],
                "links": [],
                "phones": []
            },
            "persona": "victim"
        }
    return SESSIONS[session_id]
