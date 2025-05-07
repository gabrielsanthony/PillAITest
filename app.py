import streamlit as st
import openai
import time

st.set_page_config(page_title="Pill-AI", page_icon="💊")

openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # REPLACE THIS

st.image("pillai_logo.png", width=100)
st.markdown("<h1 style='text-align:center; color:#FF6600;'>💊 Pill-AI</h1>", unsafe_allow_html=True)

if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

user_input = st.chat_input("Ask about a medicine...")
if user_input:
    st.chat_message("user").write(user_input)

    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID
    )

   with st.spinner("Pill-AI is thinking..."):
    max_wait_time = 60  # seconds
    start_time = time.time()

    while True:
        run_status = openai.beta.threads.runs.retrieve(
            run.id, thread_id=st.session_state.thread_id
        )

        # Log current status
        st.write(f"Run status: {run_status.status}")

        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            st.error("❌ Assistant failed to respond. Please try again.")
            st.stop()
        elif time.time() - start_time > max_wait_time:
            st.error("⏱️ Timeout: Assistant took too long to respond.")
            st.stop()

        time.sleep(2)  # avoid hammering the API

    messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    reply = messages.data[0].content[0].text.value
    st.chat_message("assistant").write(reply)

