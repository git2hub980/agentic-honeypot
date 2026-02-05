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
