import streamlit as st
import requests
import sqlite3
from datetime import datetime

# Page setup
st.set_page_config(
    page_title="AI Tutor Pro",
    page_icon="🎓",
    layout="wide"
)

# Hugging Face Router API
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"

HF_TOKEN = st.secrets["HF_TOKEN"]

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


# Database setup
def init_db():
    conn = sqlite3.connect("chat_history.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        time TEXT
    )
    """)

    conn.commit()
    return conn


conn = init_db()


# AI response
def ask_ai(question):

    payload = {
        "inputs": question,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()

        if isinstance(result, list):
            return result[0]["generated_text"]

        if "error" in result:
            return result["error"]

        return "AI is busy. Try again."

    except Exception as e:
        return str(e)


# UI
st.title("🎓 AI Tutor Pro")

if "messages" not in st.session_state:
    st.session_state.messages = []


# User input
question = st.chat_input("Ask your tutor anything...")

if question:

    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("Thinking..."):

        answer = ask_ai(question)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (question,answer,time) VALUES (?,?,?)",
        (question, answer, datetime.now().strftime("%H:%M"))
    )
    conn.commit()


# Display chat
for msg in st.session_state.messages:

    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])

    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])
