import streamlit as st
import openai
import time
import re
from openai import OpenAIError
import streamlit.components.v1 as components

# Page config for mobile
st.set_page_config(
    page_title="Pill-AI",
    page_icon="💊",
    layout="centered"
)

# Mobile-like app bar
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

# Logo (optional)
st.image("pillai_logo.png", width=100)

# Add microphone button for speech-to-text input
components.html("""
<button onclick="startDictation()">🎤 Speak</button>
<script>
function startDictation() {
  var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    const inputBox = window.parent.document.querySelector('input[type="text"]');
    const inputEvent = new Event('input', { bubbles: true });
    inputBox.value = transcript;
    inputBox.dispatchEvent(inputEvent);
  };
  recognition.start();
}
</script>
""", height=50)

# OpenAI API setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # Replace with your real assistant ID

# Thread setup
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Chat input
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
                    st.success("✅ Pill-AI has responded.")
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    st.error(f"❌ Run failed: `{run.status}`")
                    if run.last_error:
                        st.error(f"🔍 Error: {run.last_error}")
                    st.stop()
                time.sleep(1)

        # Display assistant response
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                if msg.content and hasattr(msg.content[0], "text"):
                    raw_text = msg.content[0].text.value
                else:
                    raw_text = msg.content[0].value
                clean_text = re.sub(r'【\\d+:\\d+†[^】]+】', '', raw_text)
                st.chat_message("assistant").write(clean_text.strip())

                # Speak the assistant's reply using browser TTS
                components.html(f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{clean_text.strip()}");
                    window.speechSynthesis.speak(msg);
                </script>
                """, height=0)

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)

# Footer disclaimer
st.markdown("---")
st.info("ℹ️ Pill-AI is not a substitute for medical advice. Always consult your doctor or pharmacist.")
