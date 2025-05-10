import streamlit as st
import re
from openai import OpenAIError

# Page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

# ✅ Centered, Larger Logo
st.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <img src="https://your-image-url-or-filename.png" width="200"/>
</div>
""", unsafe_allow_html=True)

# ✅ Example using uploaded file (if using Streamlit Cloud Manage Files)
# st.image("pillai_logo.png", width=200)

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

                # Remove source references
                cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)

                # Display result
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

