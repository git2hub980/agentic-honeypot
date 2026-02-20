agentic-honeypot is a modular scam detection and engagement system designed to:

- Detect suspicious conversational patterns
- Calculate progressive scam confidence
- Extract actionable scam intelligence
- Engage malicious actors (honeypot mode)

The system is lightweight, interpretable and designed for real-time deployment.

Core Components:

1) FastAPI Server
- Handles incoming messages
- Maintains conversation history
- Returns structured JSON response

2)Progressive Confidence Engine
- Weighted keyword scoring
- Conversation-length escalation
- Normalized confidence (0.0 – 1.0)

3) LLM Engagement Module
- Generates adaptive responses
- Simulates victim behavior based on confidence score (honeypot mode)

4) Intelligence Extraction Layer
- Regex-based entity extraction
- Identifies phone numbers, UPI IDs, emails, URLs, bank account

5) Callback System
- Triggered at high confidence threshold
- Sends structured scam intelligence to monitoring endpoint



  SYSTEM FLOW
  
Incoming Message

      ↓
Language Detection

      ↓
Text Normalization (lowercase / cleanup)

      ↓
Progressive Confidence Scoring

      ↓
If confidence > 0.7 → Enable Intelligence Extraction

      ↓
If confidence > 0.9 OR long interaction → Trigger Callback

      ↓
LLM Engagement (language-aware)

      ↓
Return JSON Response

