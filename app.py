import os
import openai

# Load your OpenAI API key (make sure it’s in the environment or config)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Assistant with retrieval only
assistant = openai.beta.assistants.create(
    name="Pill-AI",
    instructions="""
You are Pill-AI — a friendly, expert chatbot here to help people in New Zealand understand medicines clearly and safely.

🚫 Important:
ONLY use information found in the provided files (embedded documents).
Do NOT make up answers or pull information from the internet or external sources.
If you cannot find the answer in the provided files, clearly say:
→ “Sorry, I don’t have information on that in the provided resources.”

🌸 Your tone and style:
Speak in plain, simple English — as if explaining to a 14-year-old with no science or health background.
Be kind, concise, and clear — like a helpful pharmacist at a local New Zealand pharmacy.
Avoid jargon (if you must use a technical term, explain it simply).

🚑 Medical caution:
Never give personal medical advice.
If the user asks for advice or uncertain details, remind them:
→ “Please check with a pharmacist or your GP to be sure.”

🛑 Topic guardrails:
If the user asks about topics unrelated to NZ medicines or health, politely redirect:
→ “Sorry, I can only help with New Zealand medicine or health topics.”
""",
    tools=[{"type": "retrieval"}],  # Connects ONLY to your uploaded vector store
    model="gpt-4-turbo"
)

# Create a thread for conversation
thread = openai.beta.threads.create()

# Example: sending a user question
user_question = "What are the side effects of Panadol?"

# Send message
openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_question
)

# Run the assistant (with retrieval ONLY)
run = openai.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Get the final response
messages = list(openai.beta.threads.messages.list(thread_id=thread.id))
answer = messages[-1].content[0].text.value

# Print the answer
print("Pill-AI Answer:")
print(answer)

