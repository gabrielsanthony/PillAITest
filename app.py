import streamlit as st
import openai
import os
import re

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key is not configured.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# Strict system prompt
system_prompt = (
    "You are Pill-AI, a friendly expert chatbot that ONLY answers questions based on the provided CONTEXT below. "
    "If the CONTEXT does not include the answer, reply ONLY with: 'Sorry, I don’t have information on that.' "
    "Never answer from general knowledge, even if you know the answer. "
    "You help people in New Zealand understand medicines clearly, kindly, and safely in plain language a 14-year-old can understand."
)

# Streamlit page setup
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")
st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.image("pillai_logo.png", width=200)
st.markdown("</div>", unsafe_allow_html=True)

st.title("Pill-AI 💊")

# User input
user_question = st.text_input("Type your medicine question here:")

if st.button("Send"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving relevant information..."):
            try:
                # TODO: Replace this with your actual retrieval function
                # This is where you pull top 3-5 chunks from your vector store (not from OpenAI or internet)
                retrieved_context = "..."  # e.g., combine top N retrieved chunks here

                if not retrieved_context or retrieved_context.strip() == "":
                    st.write("Sorry, I don’t have information on that.")
                else:
                    # Send to OpenAI
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"CONTEXT:\n{retrieved_context}\n\nQUESTION:\n{user_question}"}
                        ],
                        temperature=0
                    )
                    answer = response.choices[0].message.content.strip()
                    cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)
                    st.write(cleaned_answer)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Disclaimer
st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
    Pill-AI is not a substitute for professional medical advice. Always check with a pharmacist or GP if unsure.
</div>
""", unsafe_allow_html=True)
