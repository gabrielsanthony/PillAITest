import openai
import streamlit as st
import time
from openai import OpenAIError

openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_XXXXXXX"  # Replace with your real assistant ID

# Create thread once
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

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
                st.write(f"🔄 Run status: `{run.status}`")

                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    st.error(f"❌ Run failed: `{run.status}`")
                    if run.last_error:
                        st.error(f"🔍 Error details: {run.last_error}")
                    st.stop()

                time.sleep(1)

            # Display assistant reply
            messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    st.chat_message("assistant").write(msg.content[0].text.value)

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)
