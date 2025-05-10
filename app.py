import streamlit as st
import re
from openai import OpenAIError

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Header with optional background
st.markdown("""
<div style='
    background-color: #FF6600;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
'>
</div>
""", unsafe_allow_html=True)

# ✅ Option 1: If you uploaded "pillai_logo.png" via Streamlit Cloud Manage Files
st.image("pillai_logo.png", width=100)

# ✅ Option 2: Use a public image URL (uncomment and replace the URL if needed)
# st.image("https://upload.wikimedia.org/wikipedia/commons/4/4f/OpenAI_Logo.svg", width=100)

# User input field
user_question = st.text_input("Type your question here:")

# Process button
if st.button("Send"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            try:
                # Example API response (replace with your actual OpenAI API call)
                answer = "You're taking metformin ."

                # Remove any source references
                cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)

                # Display the result
                st.write(cleaned_answer)

            except OpenAIError as e:
                st.error(f"Error from OpenAI API: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Disclaimer at the bottom
st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
    Pill-AI is not a substitute for professional medical advice.
</div>
""", unsafe_allow_html=True)

