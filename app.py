import streamlit as st
import openai
import os
import re
from googletrans import Translator

# Streamlit page config
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Translator setup
translator = Translator()

# Centered logo
st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.image("pillai_logo.png", width=200)
st.markdown("</div>", unsafe_allow_html=True)

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key is not configured.")
    st.stop()

openai.api_key = api_key

# Assistant ID (replace with your actual Assistant ID)
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"

# Language toggle
language = st.radio("Choose language for the answer:", ["English", "Te Reo Māori"])

# Input section
st.title("💊 Pill-AI — Your Medicine Helper")
st.write("Ask a medicine-related question below. Remember, answers come only from loaded Medsafe resources!")

user_question = st.text_input("Type your medicine question here:")

if st.button("Send"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                # Create thread if not already created
                if "thread_id" not in st.session_state:
                    thread = openai.beta.threads.create()
                    st.session_state["thread_id"] = thread.id

                # Add user message
                openai.beta.threads.messages.create(
                    thread_id=st.session_state["thread_id"],
                    role="user",
                    content=user_question
                )

                # Run assistant
                run = openai.beta.threads.runs.create(
                    thread_id=st.session_state["thread_id"],
                    assistant_id=ASSISTANT_ID
                )

                # Wait for completion
                while True:
                    run_status = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id
                    )
                    if run_status.status in ["completed", "failed"]:
                        break

                if run_status.status == "completed":
                    # Get latest assistant message
                    messages = openai.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
                    latest = messages.data[0]
                    raw_answer = latest.content[0].text.value

                    # Strip citations like  
                    cleaned_answer = re.sub(r'【[^】]*】', '', raw_answer).strip()

                    if language == "Te Reo Māori":
                        translated = translator.translate(cleaned_answer, dest='mi').text
                        st.write(translated)
                    else:
                        st.write(cleaned_answer)
                else:
                    st.error("Sorry, the assistant failed to complete the request.")

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Disclaimer
st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
Pill-AI is not a substitute for professional medical advice. Always consult a pharmacist or GP.
</div>
""", unsafe_allow_html=True)
