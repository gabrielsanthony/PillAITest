import streamlit as st
import openai
import os
import re
from googletrans import Translator
import time

# Set Streamlit page config
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Translator setup
translator = Translator()

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key is not configured.")
    st.stop()

openai.api_key = api_key

# Assistant ID
ASSISTANT_ID = "your_assistant_id_here"

# Store thread across session
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state["thread_id"] = thread.id

# Language toggle
language = st.radio("Choose language for the answer:", ["English", "Te Reo Māori"])

st.title("💊 Pill-AI — Your Medicine Helper")
st.write("Ask a medicine-related question below. Answers only come from Medsafe resources!")

user_question = st.text_input("Type your medicine question here:")

if st.button("Send"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                openai.beta.threads.messages.create(
                    thread_id=st.session_state["thread_id"],
                    role="user",
                    content=user_question
                )

                run = openai.beta.threads.runs.create(
                    thread_id=st.session_state["thread_id"],
                    assistant_id=ASSISTANT_ID
                )

                # Add timeout loop (max 20 sec)
                for _ in range(20):
                    run_status = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id
                    )
                    if run_status.status in ["completed", "failed"]:
                        break
                    time.sleep(1)
                else:
                    st.error("Timeout: Assistant did not respond.")
                    st.stop()

                if run_status.status == "completed":
                    messages = openai.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
                    latest = messages.data[0]
                    raw_answer = latest.content[0].text.value
                    cleaned_answer = re.sub(r'【[^】]*】', '', raw_answer).strip()

                    if language == "Te Reo Māori":
                        translated = translator.translate(cleaned_answer, dest='mi').text
                        st.write(translated)
                    else:
                        st.write(cleaned_answer)
                else:
                    st.error("Assistant failed to complete the request.")

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
Pill-AI is not a substitute for professional medical advice. Always consult a pharmacist or GP.
</div>
""", unsafe_allow_html=True)
