

# In-memory session store
SESSIONS = {}

def get_session(session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "id": session_id,
            "history": [],
            "intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phones": [],
                "links": [],
                "emails": []
            },
            "confidence": 0,
            "language": "en",
            "persona": None,
            "red_flags": [],
            "used_replies": [],
            "goals_asked": []
        }

    return SESSIONS[session_id]
