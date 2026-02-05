SESSIONS = {}

def get_session(session_id):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "history": [],
            "confidence": 0.0,
            "messages": 0,
            "persona":"normal",
            "used_replies":[],
            "language":"en",
            "intelligence": {
                "upiIds": [],
                "links": [],
                "phones": [],
                "bankAccounts":[],
                "suspiciousKeywords":[]
            }
        }
    return SESSIONS[session_id]
