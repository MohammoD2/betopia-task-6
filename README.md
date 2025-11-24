## Website Conversation AI · Task 6

Lightweight SDR-style orchestration that greets visitors, captures three core qualification answers, summarizes the chat, and emits a structured JSON lead. The workflow stays in persona as a helpful sales development rep (SDR) whether you launch it in Streamlit, run the CLI helper, or wire it up through FastAPI.

### Why it works
- **Guided SDR flow** — every entry point greets the visitor, asks at least three qualification questions (name, company, pain/challenges), and keeps the persona consistent.
- **Summaries + JSON** — the conversation history is condensed to 2‑3 SDR sentences and turned into a download-ready JSON object containing `name`, `email`, `company`, `role`, `pain_points`, `interested_product`, and `conversation_summary`.
- **Reusable building blocks** — `App.py` (Streamlit UI), `Local_Conversation AI.py` (CLI demo), and `Conversation AI_API.py` (FastAPI) all rely on the same OpenRouter helper so you can deploy the flavor that best fits an interview demo.

### Quick start
1. `python -m venv venv && venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Set `OPENROUTER_API_KEY` in `.env` or `streamlit secrets`.
4. Pick a surface:
   - Streamlit UI: `streamlit run App.py`
   - CLI walkthrough: `python "Local_Conversation AI.py"`
   - API: `uvicorn "Conversation AI_API:app" --reload`

### Sample conversation (Streamlit / CLI)
```
Bot: Hey there! I'm Nova, your AI SDR at Betopia. Happy to learn more—what's your full name?
You: Priya Kulkarni
Bot: Great to meet you, Priya. Which company are you representing today?
You: HorizonLabs
Bot: Awesome. Before we dive deeper, what challenges are you trying to solve around customer retention?
You: Our support team can’t keep up with inbound questions, so churn is creeping up.
Bot: Got it. Any product or solution from Betopia catching your eye so far?
You: Intelligent self-service chat.
```

### Generated lead JSON
```json
{
  "name": "Priya Kulkarni",
  "email": "ops@horizonlabs.io",
  "company": "HorizonLabs",
  "role": "Head of CX",
  "pain_points": "Support volume overload causing churn risk.",
  "interested_product": "Intelligent self-service chat",
  "conversation_summary": "Priya from HorizonLabs needs faster customer support coverage to reduce churn and is evaluating Betopia's self-service chat."
}
```

### Interview talking points
- Deterministic persona prompt keeps the SDR tone consistent across UI, CLI, and API.
- Session state + download button in `App.py` emulate a mini lead desk for recruiters to click through.
- FastAPI endpoint `/get_summary` shows how the same orchestration converts raw chat logs into structured CRM-ready payloads.

