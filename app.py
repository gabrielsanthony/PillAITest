import streamlit as st
import openai
import re
import os

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Centered, larger logo
st.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <img src="https://your-image-url-or-filename.png" width="200"/>
</div>
""", unsafe_allow_html=True)

# Set your OpenAI API key securely via Streamlit secrets or environment variable
openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# User input field
user_question = st.text_input("Type your question here:")

# Process button
if st.button("Send"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    elif not openai.api_key:
        st.error("OpenAI API key is not configured.")
    else:
        with st.spinner("Processing..."):
            try:
                # Call OpenAI API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful medicine chatbot."},
                        {"role": "user", "content": user_question}
                    ],
                    temperature=0.2
                )

                answer = response.choices[0].message.content.strip()

                # Remove source references if present
                cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)

                st.write(cleaned_answer)

            except openai.OpenAIError as e:
                st.error(f"Error from OpenAI API: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Disclaimer
st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
    Pill-AI is not a substitute for professional medical advice.
</div>
""", unsafe_allow_html=True)
