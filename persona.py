def choose_persona(confidence, history):
    if confidence > 0.6 and len(history) > 4:
        return "nephew"   # Good Cop / Tech Persona
    return "victim"

def persona_prompt(persona):
    if persona == "nephew":
        return "You are tech-savvy but helpful. Explain confusion."
    return "You are calm, cooperative, busy, not suspicious."
