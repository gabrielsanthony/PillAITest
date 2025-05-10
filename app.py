import streamlit as st
import openai
import time
import re
from openai import OpenAIError
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Centered Logo as Header
st.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <img src="pillai_logo.png" width="180">
</div>
""", unsafe_allow_html=True)

# Center Content Block for Mobile
st.markdown("<div style='max-width: 600px; margin: auto;'>", unsafe_allow_html=True)

# OpenAI Setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"

# Thread Setup
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Input field with character limit
user_input = st.text_input(
    "Ask about a medicine...",
    key="manual_input",
    placeholder="e.g. Can I take 2 paracetamol tablets?",
    help="Type your medicine question here (Max 300 characters)"
)
send = st.button("📤 Send", use_container_width=True)

# Start Over Button
if st.button("🔄 Start Over", use_container_width=True):
    st.session_state.clear()
    st.experimental_rerun()

# Character limit enforcement
if send and len(user_input) > 300:
    st.warning("⚠️ Please limit your question to 300 characters.")
elif send and user_input:
    # User Message Bubble
    st.markdown(f"""
    <div style='
        background-color: #FF6600;
        color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        word-wrap: break-word;
    '>
        You: {user_input.strip()}
    </div>
    """, unsafe_allow_html=True)

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
                    st.success("✅ Pill-AI has responded.")
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    st.error(f"❌ Run failed: `{run.status}`")
                    if run.last_error:
                        st.error(f"🔍 Error: {run.last_error}")
                    st.stop()
                time.sleep(1)
            else:
                st.error("⏱️ Assistant took too long to respond. Please try again.")
                st.stop()

        # Display assistant response
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        found_response = False
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                found_response = True
                raw_text = getattr(msg.content[0], "text", msg.content[0]).value
                clean_text = re.sub(r'【\\d+:\\d+†[^】]+】', '', raw_text)

                # Assistant Message Bubble
                st.markdown(f"""
                <div style='
                    background-color: #F1F1F1;
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px 0;
                    word-wrap: break-word;
                '>
                    Pill-AI: {clean_text.strip()}
                </div>
                """, unsafe_allow_html=True)

                # Optional voice output
                components.html(f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{clean_text.strip()}");
                    window.speechSynthesis.speak(msg);
                </script>
                """, height=0)

        if not found_response:
            st.warning("🤖 Assistant completed, but no message was returned.")

        # Auto-scroll to bottom
        components.html("<script>window.scrollTo(0, document.body.scrollHeight);</script>", height=0)

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)

# Sticky Footer Disclaimer
st.markdown("""
<style>
.sticky-footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #FF6600;
    color: white;
    text-align: center;
    padding: 5px;
}
</style>
<div class='sticky-footer'>
    ℹ️ Pill-AI is not a substitute for medical advice. Always consult your doctor or pharmacist.
</div>
""", unsafe_allow_html=True)

# Close the centered content block
st.markdown("</div>", unsafe_allow_html=True)
