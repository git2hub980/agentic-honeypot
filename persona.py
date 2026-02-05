
def choose_persona(confidence, history):
    if confidence > 0.8:
        return "failure"
    elif confidence > 0.6:
        return "suspicious"
    else:
        return "normal"
