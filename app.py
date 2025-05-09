import streamlit as st
import openai
import time
import re
from openai import OpenAIError
import streamlit.components.v1 as components

# Page config for mobile feel
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# App header bar
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

# Hidden field to receive spoken text
spoken_input = st.text_input("Speech input", key="speech_capture", label_visibility="collapsed")

# Mic button with voice-to-text
components.html("""
<button onclick="startDictation()" style="
  font-size: 18px;
  background-color: #FF6600;
  border: none;
  padding: 10px 20px;
  border-radius: 30px;
  color: white;
  cursor: pointer;">
  🎤 Speak
</button>
<script>
function startDictation() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    const iframe = window.parent.document.querySelector("iframe");
    if (!iframe) return;
    const inputBox = iframe.contentWindow.document.querySelector('input[data-testid="stTextInput"]');
    if (inputBox) {
      inputBox.value = transcript;
      inputBox.dispatchEvent(new Event("input", { bubbles: true }));
    }
  };
  recognition.start();
}
</script>
""", height=120)

# OpenAI setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # Replace with your actual Assistant ID

# Thread setup
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Combined input: either typed or from mic
user_input = st.chat_input("Ask about a medicine...", value=spoken_input)

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

        # Fetch assistant response
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                if msg.content and hasattr(msg.content[0], "text"):
                    raw_text = msg.content[0].text.value
                else:
                    raw_text = msg.content[0].value
                clean_text = re.sub(r'【\\d+:\\d+†[^】]+】', '', raw_text)
                st.chat_message("assistant").write(clean_text.strip())

                # Voice output (assistant reads answer)
                components.html(f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{clean_text.strip()}");
                    window.speechSynthesis.speak(msg);
                </script>
                """, height=0)

        # Optional: clear spoken input after use
        st.session_state["speech_capture"] = ""

    except OpenAIError as e:
        st.error("⚠️ OpenAI API error occurred.")
        st.exception(e)

# Disclaimer
st.markdown("---")
st.info("ℹ️ Pill-AI is not a substitute for medical advice. Always consult your doctor or pharmacist.")
