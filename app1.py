# To run: pip install streamlit google-genai python-dotenv

import os
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types

# ----------------------------
# 🔧 Setup
# ----------------------------
load_dotenv()
st.set_page_config(page_title="Agno Gemini Chatbot", page_icon="🤖", layout="centered")
st.sidebar.header("⚙️ Model Settings")
model_choice = st.sidebar.selectbox(
    "Select Gemini Model:",
    ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
    index=1
)

# ----------------------------
# 🧠 Initialize Gemini Client
# ----------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Always enable Google Search tool
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool],
    thinking_config=types.ThinkingConfig(thinking_budget=-1),
)

# ----------------------------
# 💬 Chat History
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# ✍️ Chat Input
# ----------------------------
if prompt := st.chat_input("💬 Ask me anything..."):
    # Display user query
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching and thinking... 🔎🤔"):
            try:
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    ),
                ]

                # Generate grounded structured answer
                response = client.models.generate_content(
                    model=model_choice,
                    contents=contents,
                    config=config,
                )

                if hasattr(response, "text") and response.text:
                    answer = response.text
                else:
                    answer = "⚠️ No response received from the Gemini model."

            except Exception as e:
                answer = f"❌ Error: {e}"

            st.markdown(answer)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})

