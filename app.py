import streamlit as st
import openai
import time
import re
from openai import OpenAIError
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Header
st.markdown("""
<div style='
    background-color: #FF6600;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    color: white;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
'>
    Pill-AI Assistant
</div>
""", unsafe_allow_html=True)

# Logo
st.image("pillai_logo.png", width=100)

# OpenAI setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"

# Thread setup
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Input field and Send button
user_input = st.text_input("Ask about a medicine...", key="manual_input")
send = st.button("📤 Send")

# Determine final input source
final_input = None
if send:
    final_input = st.session_state["manual_input"]
#elif spoken_input and not st.session_state["manual_input"]:
#    final_input = spoken_input
  #  st.session_state["speech_capture"] = ""

# Run assistant logic
if final_input:
    st.chat_message("user").write(final_input)

    try:
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=final_input
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
                st.chat_message("assistant").write(clean_text.strip())

                # Voice output
                components.html(f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{clean_text.strip()}");
                    window.speechSynthesis.speak(msg);
                </script>
                """, height=0)

        if not found_response:
            st.warning("🤖 Assistant completed, but no message was returned.")

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)

# Footer disclaimer
st.markdown("---")
st.info("ℹ️ Pill-AI is not a substitute for medical advice. Always consult your doctor or pharmacist.")
