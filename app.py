import streamlit as st
import openai
import time
from openai import OpenAIError

st.set_page_config(page_title="Pill-AI", page_icon="💊")

openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # REPLACE THIS

st.image("pillai_logo.png", width=100)
st.markdown("<h1 style='text-align:center; color:#FF6600;'>💊 Pill-AI</h1>", unsafe_allow_html=True)

# Step 1: Create a thread if not already created
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Step 2: Capture user input
user_input = st.chat_input("Ask about a medicine...")
if user_input:
    st.chat_message("user").write(user_input)

 try:
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
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    st.error(f"❌ Run failed: {run.status}")
                    if run.last_error:
                        st.error(run.last_error)
                    st.stop()
                time.sleep(1)

            messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    st.chat_message("assistant").write(msg.content[0].text.value)

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)
