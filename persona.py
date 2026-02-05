def choose_persona(confidence: float) -> dict:
    """
    Persona layer is now only a behavior controller.
    It does NOT decide language or replies.
    """

    if confidence >= 0.9:
        return {
            "allow_reply": True,
            "force_failure": True
        }

    return {
        "allow_reply": True,
        "force_failure": False
    }
