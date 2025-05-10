import streamlit as st
import re
from openai import OpenAIError

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# Header styling
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

# Display the uploaded logo (replace the filename with your uploaded file name)
st.image("1c9f6e6b-1414-4bf9-9591-70d89bdab95e.png", width=100)

# User input
user_question = st.text_input("Type your question here:")

# Process button
if st.button("Send"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            try:
                # Example simulated response
                answer = "You're taking metformin ."

                # Remove source references
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
