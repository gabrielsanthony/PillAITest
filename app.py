import streamlit as st
import openai
import time
import re  # ✅ Add this
from openai import OpenAIError


# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊")

# Display logo and title
st.image("pillai_logo.png", width=100)  # Make sure this file exists in the same folder
st.markdown("<h1 style='text-align:center; color:#FF6600;'>💊 Pill-AI</h1>", unsafe_allow_html=True)

# OpenAI setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # Replace with your actual Assistant ID

# Thread creation
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Chat input
user_input = st.chat_input("Ask about a medicine...")
if user_input:
    st.chat_message("user").write(user_input)

    try:
        # Add user message to the thread
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

            # Wait for completion
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

            # Clean citations like  
            clean_text = re.sub(r'【\d+:\d+†[^】]+】', '', msg.content[0].text.value)
            
            # Show assistant response
            messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    clean_text = re.sub(r'【\d+:\d+†[^】]+】', '', msg.content[0].text.value)
                    st.chat_message("assistant").write(clean_text.strip())

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)

# Optional footer/disclaimer
st.markdown("---")
st.info("ℹ️ Pill-AI is not a substitute for professional medical advice. Always consult your local Pharmacist.")
