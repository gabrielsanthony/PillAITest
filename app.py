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

# Hidden speech input field
spoken_input = st.text_input("Speech input", key="speech_capture", label_visibility="collapsed")

# Mic button (press once to speak)
components.html("""
<style>
#voice-button {
  font-size: 18px;
  background-color: #FF6600;
  border: none;
  padding: 10px 20px;
  border-radius: 30px;
  color: white;
  cursor: pointer;
}
</style>

<button id="voice-button">🎤 Press to Speak</button>

<script>
let recognition;
const button = document.getElementById("voice-button");

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

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

  recognition.onerror = function(event) {
    alert("Speech recognition error: " + event.error);
  };

  button.onclick = () => recognition.start();
}
</script>
""", height=150)

st.caption("🗣️ Press to speak, then press Send to submit.")

# OpenAI API setup
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_3xS1vLEMnQyFqNXLTblUdbWS"

# Thread setup
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

# Text input + visible Send button
user_input = st.text_input("Ask about a medicine...", key="manual_input")
send = st.button("📤 Send")

# Choose final input source
final_input = None
if send:
    final_input = st.session_state["manual_input"]
elif spoken_input and not st.session_state["manual_input"]:
    final_input = spoken_input
    st.session_state["speech_capture"] = ""

# Run assistant
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
                        st.error(f"🔍 Error: {run.last_error_
