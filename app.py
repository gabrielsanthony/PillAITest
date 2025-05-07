import streamlit as st
import openai

st.set_page_config(page_title="Pill-AI", page_icon="💊")

openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "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"  # REPLACE THIS

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
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                run.id, thread_id=st.session_state.thread_id
            )
            if run_status.status == "completed":
                break

    messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    reply = messages.data[0].content[0].text.value
    st.chat_message("assistant").write(reply)

