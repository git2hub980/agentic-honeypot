def choose_persona(session) -> dict:
    confidence = session.get("confidence", 0)
    engagement = session.get("engagement_score", 0)
    messages = session.get("messages", 0)

    persona = {
        "allow_reply": True,
        "force_failure": False,
        "style": "neutral"
    }

    # 🔥 High scam confidence → waste scammer time
    if confidence > 0.7:
        persona["style"] = "confused"
        session["agent_notes"].append("Switching to confused persona")
    
    # 🔥 Very high confidence → simulate transaction failures
    if confidence > 0.9:
        persona["force_failure"] = True
        session["agent_notes"].append("Triggering repeated failure loop")

    # 🔥 Long conversation → increase emotional engagement
    if messages > 8:
        persona["style"] = "emotionally_invested"
        session["agent_notes"].append("Increasing emotional hook")

    # 🔥 Low engagement → act cooperative
    if engagement < 4:
        persona["style"] = "cooperative"
        session["agent_notes"].append("Acting cooperative to build trust")

    return persona
