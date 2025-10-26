import os
import time
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from textwrap import dedent

load_dotenv()

# ----------------------------
# 🌐 Streamlit UI setup
# ----------------------------
st.set_page_config(page_title="Agno", page_icon="🪅", layout="centered")
st.markdown(
    "<h3><span style='color: #fc4503;'>⚡Agno </span><span style='color: #0313fc;'>Gemini</span> Chatbot"
    "<img src='https://logos-world.net/wp-content/uploads/2025/01/Bard-Logo-2023.png' width='50'></h3>",
    unsafe_allow_html=True,
)

# Sidebar - Model selection
st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose Gemini Model",
    ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
    index=0
)

# Initialize agent
agent = Agent(
    model=Gemini(id=model_choice, api_key=os.getenv("GEMINI_API_KEY"), search=True),
    description=dedent("""You are a helpful assistant with access to web search via Google Search API."""), 
    instructions=dedent("""Use the web search tool to answer user queries."""), 
    markdown=True,
)

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("💬 Ask me anything..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"{prompt}")

    # Assistant streaming response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Call agent
        response = agent.run(prompt)

        # Simulate streaming typing with Pac-Man cursor 🍒
        for chunk in response.content.split():
            full_response += chunk + " "
            message_placeholder.markdown(
                full_response + " <img src='https://media.tenor.com/HiVVJv-skJcAAAAM/pac-man.gif' width='22' style='vertical-align: middle;'/>",
                unsafe_allow_html=True
            )
            time.sleep(0.05)

        # Final text without cursor
        message_placeholder.markdown(full_response)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
