import streamlit as st
import sqlite3
import pandas as pd
import requests
import time
from datetime import datetime

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="AI Student Tutor Pro",
    page_icon="🎓",
    layout="wide"
)

# Secure Token & API Setup
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
# Replace the hardcoded token with st.secrets for safety
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except:
    HF_TOKEN = "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" # Fallback (not recommended for public)

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

class StudentTutorPro:
    def __init__(self):
        self.conn = self.init_db()
        self.subject_prompts = {
            "Mathematics": "You are a math tutor. Solve step by step.",
            "Programming": "You are a Python programming tutor. Provide code examples.",
            "Electrical Engineering": "You are an electrical engineering tutor.",
            "General": "You are a helpful tutor."
        }

    def init_db(self):
        conn = sqlite3.connect("student_tutor_pro.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT, answer TEXT, subject TEXT, timestamp TEXT
        )""")
        conn.commit()
        return conn

    def detect_subject(self, question):
        q = question.lower()
        if any(word in q for word in ["math","algebra","calculus","derivative"]): return "Mathematics"
        if any(word in q for word in ["python","code","program","loop"]): return "Programming"
        if any(word in q for word in ["motor","transformer","voltage","current"]): return "Electrical Engineering"
        return "General"

    def get_ai_response(self, question):
        subject = self.detect_subject(question)
        prompt = f"{self.subject_prompts[subject]}\n\nQuestion: {question}"
        payload = {"inputs": prompt, "options": {"wait_for_model": True}} # Tells HF to wait if loading
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            result = response.json()
            
            # Handle the specific way Flan-T5 returns text
            if isinstance(result, list) and len(result) > 0:
                answer = result[0].get("generated_text", "I couldn't generate an answer.")
            elif "error" in result:
                answer = f"AI Error: {result['error']}"
            else:
                answer = "The AI is currently busy. Please try again in a moment."
        except Exception as e:
            answer = f"Connection Error: {str(e)}"

        return answer, subject

    def save_chat(self, question, answer, subject):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO chats (question,answer,subject,timestamp) VALUES (?,?,?,?)",
            (question, answer, subject, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.conn.commit()

# Main App Logic
def main():
    app = StudentTutorPro()
    st.markdown('<h1 style="color:#1f77b4;">🎓 AI Student Tutor Pro</h1>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    question = st.text_input("Ask your tutor anything (Math, Circuits, Coding...):")

    if st.button("Get Answer"):
        if question:
            with st.spinner("AI is thinking... (may take a moment to wake up)"):
                answer, subject = app.get_ai_response(question)
                app.save_chat(question, answer, subject)
                st.session_state.chat_history.append({
                    "question": question, "answer": answer,
                    "subject": subject, "time": datetime.now().strftime("%H:%M")
                })

    if st.session_state.chat_history:
        st.subheader("Latest Answer")
        latest = st.session_state.chat_history[-1]
        st.info(f"**Subject:** {latest['subject']}")
        st.write(latest["answer"])

    if st.session_state.chat_history:
        st.subheader("History")
        for chat in st.session_state.chat_history[::-1]:
            with st.expander(f"{chat['time']} - {chat['subject']}"):
                st.write(f"**Q:** {chat['question']}")
                st.write(f"**A:** {chat['answer']}")

if __name__ == "__main__":
    main()
