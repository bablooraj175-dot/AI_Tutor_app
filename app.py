import streamlit as st
import google.generativeai as genai
import pandas as pd
import altair as alt
import random

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

# Page config
st.set_page_config(
    page_title="AI Tutor Pro",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Student Tutor")
st.write("Ask me any question and I will help you learn!")

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar subject selector
st.sidebar.header("Tutor Settings")

subject = st.sidebar.selectbox(
    "Choose Subject",
    ["General", "Math", "Science", "Programming", "History"]
)

# Dynamic chart
st.subheader("📊 Weekly Learning Activity")

data = pd.DataFrame({
    "Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "Questions": [random.randint(1,10) for _ in range(7)]
})

chart = alt.Chart(data).mark_bar().encode(
    x="Day",
    y="Questions",
    color="Questions"
)

st.altair_chart(chart, use_container_width=True)

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
prompt = st.chat_input("Ask your tutor a question...")

if prompt:

    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response = model.generate_content(
                f"You are an expert tutor helping students learn {subject}. "
                f"Explain clearly with examples.\n\nQuestion: {prompt}"
            )

            answer = response.text

            st.write(answer)

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })

st.markdown("---")
st.caption("AI Tutor • Powered by Google Gemini + Streamlit")
