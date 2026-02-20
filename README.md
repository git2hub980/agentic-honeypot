## Description

Agentic-Honeypot is an adaptive scam detection and engagement system designed to
identify malicious conversational intent in real time.

Unlike static keyword filters, the system uses progressive confidence scoring,
behavioral red-flag analysis, and dynamic engagement strategies to:

- Detect scam intent early
- Extract structured intelligence (financial & communication artifacts)
- Sustain engagement to gather deeper evidence
- Safely escalate and report confirmed scam sessions

The architecture is modular, interpretable, and optimized for real-time API deployment.


## Approach

### Scam Detection
The system calculates scam probability using:
- Progressive keyword weighting
- Red-flag pattern recognition
- Escalation based on conversational depth
- Behavioral signals (urgency, reward bait, banking references)

Confidence is normalized between 0.0 – 1.0.

## Core Components:

1) FastAPI Server
- Handles incoming messages
- Maintains conversation history
- Returns structured JSON response

2) Progressive Confidence Engine
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


## Key Features

- Progressive scam confidence (conversation-aware, not keyword-only)
- Risk-weighted intelligence scoring
- Structured intelligence extraction (OTP, IFSC, UPI, bank accounts, links)
- Agentic honeypot engagement strategy
- Automated high-confidence reporting callback
- Language-aware detection
- Lightweight, explainable architecture


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

### Intelligence Extraction
Upon suspicious detection, the system extracts:
- Phone numbers
- UPI IDs
- Bank account numbers
- IFSC codes
- OTP codes
- Email addresses
- Phishing URLs

Extraction is rule-based (regex) to ensure determinism and explainability.

### Engagement Strategy
When confidence rises:
- The honeypot simulates a potential victim
- Gradually responds to prolong interaction
- Prioritizes extraction goals dynamically
- Triggers callback when threshold is reached

This prevents premature termination and maximizes intelligence capture.
