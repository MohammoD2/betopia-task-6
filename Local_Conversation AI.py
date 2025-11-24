import requests
import json
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

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
        return res_json['choices'][0]['message']['content']
    else:
        print(response.text)
        raise Exception("LLM request failed")

# ---------------------------
# Chatbot flow (guided)
# ---------------------------
def run_chatbot():
    lead = {}
    conversation = []

    # 1️⃣ Greeting
    prompt = "You are a friendly SDR bot. Greet the visitor warmly."
    greeting = get_llm_response(prompt)
    print(f"Bot: {greeting}")
    conversation.append({"role": "bot", "content": greeting})

    # 2️⃣ Collect all required fields explicitly
    questions = [
        {"field": "name", "question": "What is your full name?"},
        {"field": "email", "question": "Can I have your email address?"},
        {"field": "company", "question": "Which company are you with?"},
        {"field": "role", "question": "What is your role in the company?"},
        {"field": "pain_points", "question": "What challenges or pain points are you trying to solve?"}
    ]

    for q in questions:
        print(f"Bot: {q['question']}")
        answer = input("You: ").strip()
        lead[q['field']] = answer if answer else "Not Provided"
        conversation.append({"role": "user", "content": answer})

    # 3️⃣ Optional: Collect interested product / project info
    print("Bot: Which product or solution are you interested in?")
    answer = input("You: ").strip()
    lead["interested_product"] = answer if answer else "Not Provided"
    conversation.append({"role": "user", "content": answer})

    # 4️⃣ Generate conversation summary via LLM
    summary_prompt = f"""
    You are a helpful SDR bot. Based on the conversation below, summarize the discussion in 2-3 sentences.
    Conversation: {conversation}
    """
    lead["conversation_summary"] = get_llm_response(summary_prompt)

    # 5️⃣ Output JSON lead object
    print("\n--- Generated JSON Lead Object ---")
    print(json.dumps(lead, indent=4))


# ---------------------------
# Run chatbot
# ---------------------------
if __name__ == "__main__":
    run_chatbot()
