import streamlit as st
import openai

st.set_page_config(page_title="Pill-AI", page_icon="💊")

openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_your_assistant_id"  # REPLACE THIS

st.image("pillai_logo.png", width=100)
st.markdown("<h1 style='text-align:center; color:#FF6600;'>💊 Pill-AI</h1>", unsafe_allow_html=True)

if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

user_input = st.chat_input("Ask about a medicine...")
if user_input:
    st.chat_message("user").write(user_input)

    openai.beta.threads.messages.create(
        thread_id=_
