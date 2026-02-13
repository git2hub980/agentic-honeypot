from fastapi import FastAPI, Header, HTTPException
from language_detector import detect_language
from dotenv import load_dotenv
import os
import requests

from scam_detector import progressive_confidence
from sessions import get_session
from extractor import extract
from persona import choose_persona
from llm_engine import generate_smart_reply

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")


@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(...)):

    # 🔐 API Key Validation
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 📩 Safe Payload Extraction
        session_id = payload.get("sessionId")
        message = payload.get("message", {}).get("text")

        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Invalid payload format")

        # 🧠 Get/Create Session
        session = get_session(session_id)

        # 🌐 Multi-language detection (ML-style output)
        lang_data = detect_language(message)
        language = lang_data.get("primary", "en")

        session["language"] = language

        # 📊 Update message count
        session["messages"] += 1

        # 📈 Progressive scam confidence
        confidence = progressive_confidence(message, session["history"])
        session["confidence"] = confidence

        # 🕵️ Extract intelligence
        extract(message, session["intelligence"])

        # 🎭 Persona selection
        persona = choose_persona(confidence, session["history"])
        session["persona"] = persona

        # 📜 Store history
        session["history"].append(message)

        # 🤖 Generate reply (LLM controls extraction naturally)
        reply = generate_smart_reply(message, session)
                # 🎯 Controlled intelligence extraction (rotating, non-repetitive)
        if confidence > 0.7:

            if "extraction_step" not in session:
                session["extraction_step"] = 0

            # Ask extraction question every 3 messages only
            if session["messages"] % 3 == 0:

                extraction_questions = {
                    "en": [
                        " btw which bank is this about?",
                        " which account is linked to this?",
                        " what number is registered there?",
                        " where should i check this exactly?",
                        " can u confirm ur acc no.?",
                        " can you resend me ur upi id again?"
                    ],
                    "hi": [
                        " ye kaunsi bank ka hai?",
                        " kaunsa account linked hai?",
                        " kaunsa number registered hai?",
                        " mujhe kaha check karna chahiye?",
                    ],
                    "hinglish": [
                        " ye kaunsi bank ka scene hai?",
                        " kaunsa account linked hai isse?",
                        " kaunsa number dala hua hai?",
                        " kaha check karu main?",
                    ]
                }

                lang = session.get("language", "en")
                questions = extraction_questions.get(lang, extraction_questions["en"])

                step = session["extraction_step"] % len(questions)

                reply += questions[step]
                session["extraction_step"] += 1


        # 🚨 Final stage callback
        if confidence > 0.9 or session["messages"] > 18:
            send_final_callback(session_id, session)

        return {
            "status": "success",
            "reply": reply
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def send_final_callback(session_id, session):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session["messages"],
        "extractedIntelligence": session["intelligence"],
        "agentNotes": "Adaptive emotional multi-language honeypot with progressive intelligence extraction"
    }

    try:
        requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
    except:
        pass
