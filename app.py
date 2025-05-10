import streamlit as st
import openai
import time
import re
from openai import OpenAIError
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Header with centered logo
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
    <img src="https://your-logo-url.com/logo.png" width="100"/>
</div>
""", unsafe_allow_html=True)

# Hidden speech input field
spoken_input = st.text_input("Speech input", key="speech_capture", label_visibility="collapsed")

# Mic button (press to speak)
components.html("""
    <style>
        #voice-button {
            font-size: 18px;
            background-color: #FF6600;
            border: none;
            padding: 10px 20px;
            border-radius: 12px;
            color: white;
            cursor: pointer;
        }
    </style>
    <button id="voice-button" onclick="startRecording()">🎤 Press to Speak</button>
    <script>
        function startRecording() {
            alert("Voice recording not implemented in this demo.");
        }
    </script>
""", height=100)

# User input
user_question = st.text_input("Type your question here:")

# Process button
if st.button("Send"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            try:
                # Simulate API response for demo purposes
                answer = "You're taking metformin ."

                # Remove source references like  
                cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)

                st.write(cleaned_answer)

            except OpenAIError as e:
                st.error(f"Error from OpenAI API: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Disclaimer centered
st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
    Pill-AI is not a substitute for professional medical advice.
</div>
""", unsafe_allow_html=True)
