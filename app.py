import streamlit as st
import openai
import os
import re

# Streamlit page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Centered logo
st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.image("pillai_logo.png", width=200)
st.markdown("</div>", unsafe_allow_html=True)

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key is not configured.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# Assistant ID
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"

# Store thread across sessions
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id

# Title and description
st.title("💊 Pill-AI — Your Medicine Helper")
st.write("Ask a medicine-related question below. Remember, answers come only from loaded Medsafe resources!")

# Language selector
language = st.selectbox("Select your preferred language for the answer:", ["English", "Te Reo Māori"])

# User question input
user_question = st.text_input("Type your medicine question here (in any language):")

if st.button("Send"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                # Add language instruction if Māori selected
                language_instruction = ""
                if language == "Te Reo Māori":
                    language_instruction = " Please respond in Te Reo Māori."

                # Add message to thread
                client.beta.threads.messages.create(
                    thread_id=st.session_state["thread_id"],
                    role="user",
                    content=user_question + language_instruction
                )

                # Run assistant
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state["thread_id"],
                    assistant_id=ASSISTANT_ID
                )

                # Wait for completion
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id
                    )
                    if run_status.status in ["completed", "failed"]:
                        break

                if run_status.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
                    latest = messages.data[0]
                    raw_answer = latest.content[0].text.value

                    # Strip citations
                    cleaned_answer = re.sub(r'【[^】]*】', '', raw_answer).strip()

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

