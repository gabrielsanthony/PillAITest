import streamlit as st
import openai
import chromadb
import os
import re

# Setup Streamlit page
st.set_page_config(page_title="Pill-AI", page_icon="💊", layout="centered")

st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.image("pillai_logo.png", width=200)
st.markdown("</div>", unsafe_allow_html=True)

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    st.error("OpenAI API key is not configured.")
    st.stop()

# Connect to ChromaDB
db_path = "/content/drive/MyDrive/chroma_db"  # adjust if needed
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_or_create_collection("medsafe_embeddings")

# Retrieval function
def retrieve_top_chunks(query, top_k=5):
    results = collection.query(query_texts=[query], n_results=top_k)
    documents = results.get('documents', [[]])[0]
    if not documents:
        return None
    return "\n\n".join(documents)

# User input
user_question = st.text_input("Type your medicine question here:")

if st.button("Send"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            context = retrieve_top_chunks(user_question)
            if not context:
                st.write("Sorry, I don’t have information on that.")
            else:
                try:
                    system_prompt = (
                        "You are Pill-AI — a friendly, expert chatbot designed to help people in New Zealand understand medicines clearly and safely.\n"
                        "ONLY use the following extracted medicine information when answering the user’s question.\n"
                        "If the information is not in the provided text, respond: 'Sorry, I don’t have information on that.'\n"
                        "Speak simply, kindly, and clearly, like a helpful pharmacist.\n"
                        "NEVER pull information from outside the provided context."
                    )

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt + f"\n\nExtracted context:\n{context}"},
                            {"role": "user", "content": user_question}
                        ],
                        temperature=0.2
                    )

                    answer = response.choices[0].message.content.strip()
                    cleaned_answer = re.sub(r'【\d+:\d+†[^\】]+】', '', answer)
                    st.write(cleaned_answer)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Disclaimer
st.markdown("""
<div style='text-align: center; color: grey; margin-top: 30px;'>
    Pill-AI is not a substitute for professional medical advice. Always consult your pharmacist or GP.
</div>
""", unsafe_allow_html=True)
