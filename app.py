import streamlit as st
import openai
import os

# ✅ Set up OpenAI API key (from environment or Streamlit secrets)
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not set. Please set it as an environment variable or in Streamlit secrets.")
    st.stop()
openai.api_key = api_key

# ✅ Your existing OpenAI Assistant ID
assistant_id = "asst_3xS1vLEMnQyFqNXLTblUdbWS"  # ← replace this with your real assistant ID from OpenAI

# ✅ Streamlit page settings
st.set_page_config(page_title="Pill-AI 💊", layout="centered")
st.title("💊 Pill-AI — Your Medicine Helper")

st.markdown("Ask a medicine-related question below. Remember, answers come only from loaded Medsafe resources!")

# ✅ User input
user_question = st.text_input("Type your medicine question here:")

if st.button("Ask Pill-AI"):
    if not user_question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("💬 Pill-AI is thinking..."):
            try:
                # ✅ Create a new thread
                thread = openai.beta.threads.create()

                # ✅ Add user message to the thread
                openai.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_question
                )

                # ✅ Run the assistant on the thread
                run = openai.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=assistant_id
                )

                # ✅ Retrieve the latest assistant reply
                messages = openai.beta.threads.messages.list(thread_id=thread.id)
                last_message = messages.data[0].content[0].text.value.strip()

                st.success(last_message)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ✅ Disclaimer at the bottom
st.markdown("""
---
<div style='text-align: center; color: grey;'>
ℹ️ **Pill-AI** provides general medicine information only.  
It is not a substitute for professional medical advice.  
Please consult your pharmacist or GP for personal health questions.
</div>
""", unsafe_allow_html=True)

