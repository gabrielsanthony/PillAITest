import streamlit as st
import openai
import re
import os

# Streamlit page setup
st.set_page_config(page_title="Pill-AI 💊", page_icon="💊", layout="centered")

# App header
st.markdown("<h1 style='text-align: center;'>Pill-AI 💊</h1>", unsafe_allow_html=True)
st.write("Ask a medicine-related question below. Remember, answers come only from loaded Medsafe resources!")

# OpenAI setup
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
assistant_id = st.secrets.get("OPENAI_ASSISTANT_ID") or os.getenv("OPENAI_ASSISTANT_ID")

if not api_key or not assistant_id:
    st.error("OpenAI API key or Assistant ID is missing. Please set them in Streamlit secrets or environment variables.")
else:
    client = openai.OpenAI(api_key=api_key)

    user_question = st.text_input("Type your medicine question here:")

    if st.button("Send"):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Processing..."):
                try:
                    thread = client.beta.threads.create()
                    client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=user_question
                    )

                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant_id
                    )

                    # Wait for run completion
                    import time
                    while True:
                        status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                        if status.status == "completed":
                            break
                        elif status.status in ["failed", "cancelled"]:
                            st.error(f"Run {status.status}.")
                            break
                        time.sleep(1)

                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    answer = messages.data[0].content[0].text.value.strip()

                    # Remove citations like  
                    cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)

                    st.success(cleaned_answer)

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Disclaimer
st.markdown("<div style='text-align: center; color: grey; margin-top: 30px;'>Pill-AI is not a substitute for professional medical advice. Please consult a pharmacist or GP if unsure.</div>", unsafe_allow_html=True)

