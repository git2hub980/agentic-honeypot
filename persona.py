def choose_persona(confidence: float, history) -> dict:
    if confidence >= 0.9:
        return {"allow_reply": True, "force_failure": True}

    return {"allow_reply": True, "force_failure": False}
