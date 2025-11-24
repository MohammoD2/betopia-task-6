import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
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
        st.error(f"LLM request failed: {response.text}")
        return "Error in generating response."

# ---------------------------
# Initialize session state
# ---------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "lead" not in st.session_state:
    st.session_state.lead = {}

st.title("🤖 AI SDR Chatbot")

st.write("Welcome! I’m your friendly AI SDR bot. Let's capture your lead information.")

# ---------------------------
# Collect user info
# ---------------------------
with st.form("lead_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    company = st.text_input("Company Name")
    role = st.text_input("Role in Company")
    pain_points = st.text_area("Challenges / Pain Points")
    interested_product = st.text_input("Interested Product / Solution")
    submitted = st.form_submit_button("Submit")

if submitted:
    # Save to session
    st.session_state.lead = {
        "name": name or "Not Provided",
        "email": email or "Not Provided",
        "company": company or "Not Provided",
        "role": role or "Not Provided",
        "pain_points": pain_points or "Not Provided",
        "interested_product": interested_product or "Not Provided"
    }

    # Add to conversation history
    st.session_state.conversation.append({"role": "user", "content": f"Name: {name}"})
    st.session_state.conversation.append({"role": "user", "content": f"Email: {email}"})
    st.session_state.conversation.append({"role": "user", "content": f"Company: {company}"})
    st.session_state.conversation.append({"role": "user", "content": f"Role: {role}"})
    st.session_state.conversation.append({"role": "user", "content": f"Pain Points: {pain_points}"})
    st.session_state.conversation.append({"role": "user", "content": f"Interested Product: {interested_product}"})

    # 1️⃣ Generate conversation summary using LLM
    summary_prompt = f"""
    You are a helpful SDR bot. Based on the conversation below, summarize the discussion in 2-3 sentences.
    Conversation: {st.session_state.conversation}
    """
    st.session_state.lead["conversation_summary"] = get_llm_response(summary_prompt)

    st.success("✅ Lead captured and summarized!")

# ---------------------------
# Display conversation / lead
# ---------------------------
if st.session_state.lead:
    st.subheader("Generated JSON Lead Object")
    st.json(st.session_state.lead)

    # ---------------------------
    # Download JSON button
    # ---------------------------
    json_str = json.dumps(st.session_state.lead, indent=4)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="lead.json",
        mime="application/json"
    )

# ---------------------------
# Optional: show conversation history
# ---------------------------
if st.session_state.conversation:
    st.subheader("Conversation History")
    for msg in st.session_state.conversation:
        if msg["role"] == "bot":
            st.markdown(f"**Bot:** {msg['content']}")
        else:
            st.markdown(f"**You:** {msg['content']}")
