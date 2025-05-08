import streamlit as st
import openai
import time
import re
from openai import OpenAIError

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊")

# Display logo and title
st.image("pillai_logo.png", width=100)
st.markdown("<h1 style='text-align:center; color:#FF6600;'>💊 Pill-AI</h1>", unsafe_allow_html=True)

# OpenAI setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # Replace with your actual Assistant ID

# Create assistant thread
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# User input
user_input = st.chat_input("Ask about a medicine...")
if user_input:
    st.chat_message("user").write(user_input)

    try:
        # Add message to thread
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        with st.spinner("Pill-AI is thinking..."):
            run = openai.beta.threads.runs.create(
                assistant_id=ASSISTANT_ID,
                thread_id=st.session_state.thread_id
            )

            for _ in range(30):
                run = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

                if run.status == "completed":
                    st.success("✅ Pill-AI has responded.")
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    st.error(f"❌ Run failed: `{run.status}`")
                    if run.last_error:
                        st.error(f"🔍 Error: {run.last_error}")
                    st.stop()

                time.sleep(1)

        # Fetch and clean assistant response
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                if msg.content and hasattr(msg.content[0], "text"):
                    raw_text = msg.content[0].text.value
                else:
                    raw_text = msg.content[0].value

                clean_text = re.sub(r'【\d+:\d+†[^】]+】', '', raw_text)
                st.chat_message("assistant").write(clean_text.strip())

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)

# Footer
st.markdown("---")
st.info("ℹ️ Pill-AI is not a substitute for medical advice. Always consult your doctor or pharmacist.")

