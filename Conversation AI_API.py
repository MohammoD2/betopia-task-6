from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import json
import os

# Load environment variables (or use st.secrets later in Streamlit)
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

app = FastAPI(title="Website Conversation AI")

# ---------------------------
# In-memory storage for sessions
# ---------------------------
sessions = []

# ---------------------------
# Pydantic models
# ---------------------------
class UserAnswer(BaseModel):
    session_id: str
    question: str
    answer: str

class LeadRequest(BaseModel):
    session_id: str
    conversation_summary: str

# ---------------------------
# Helper function: OpenRouter LLM call
# ---------------------------
def get_llm_response(prompt: str) -> str:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        })
    )
    if response.status_code == 200:
        res_json = response.json()
        # Get the content of the first message from LLM
        return res_json['choices'][0]['message']['content']
    else:
        raise HTTPException(status_code=500, detail="LLM request failed")

# ---------------------------
# API endpoints
# ---------------------------

@app.get("/start_conversation")
def start_conversation(session_id: str):
    """Start conversation and return greeting."""
    # Check if session already exists
    for s in sessions:
        if s["session_id"] == session_id:
            return {"message": "Conversation already started."}
    
    prompt = "You are a friendly SDR bot. Greet the visitor naturally and ask the first qualification question."
    greeting = get_llm_response(prompt)
    
    # Save session
    sessions.append({
        "session_id": session_id,
        "conversation": [{"role": "bot", "content": greeting}],
        "answers": []
    })
    return {"message": greeting}

@app.post("/ask_question")
def ask_question(data: UserAnswer):
    """Add user answer and get next bot message."""
    # Find session
    session = next((s for s in sessions if s["session_id"] == data.session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user answer
    session["answers"].append({"question": data.question, "answer": data.answer})
    session["conversation"].append({"role": "user", "content": data.answer})
    
    # Generate next question or follow-up
    prompt = f"You are a helpful SDR. Based on the conversation so far: {session['conversation']}, ask the next qualification question or follow-up naturally."
    bot_reply = get_llm_response(prompt)
    
    session["conversation"].append({"role": "bot", "content": bot_reply})
    return {"message": bot_reply}

@app.post("/get_summary")
def get_summary(data: LeadRequest):
    """Summarize conversation and generate JSON lead object."""
    session = next((s for s in sessions if s["session_id"] == data.session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create prompt to generate JSON
    prompt = f"""
    You are a helpful SDR bot. Based on the conversation below, generate a structured JSON lead object with:
    name, email, company, role, pain_points, interested_product, conversation_summary.

    Conversation:
    {session['conversation']}
    """
    
    json_response = get_llm_response(prompt)
    
    # Save summary in session (optional)
    session["summary"] = json_response
    return {"lead": json_response}

