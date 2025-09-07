# pip install agno streamlit python-dotenv 

import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from textwrap import dedent
import time

load_dotenv()

# Streamlit UI setup
st.set_page_config(page_title="Agno", page_icon="👾", layout="centered")
st.markdown("<h1><span style='color: #fc4503;'> 👻 Agno </span><span style='color: #0313fc;'>Gemini</span> Chatbot<img src='https://logos-world.net/wp-content/uploads/2025/01/Bard-Logo-2023.png' width='70'></h1>", unsafe_allow_html=True)

# Sidebar - Model selection
st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose Gemini Model",
    ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
    index=0  # default to "gemini-2.5-flash-lite"
)

# Initialize agent dynamically based on model_choice
agent = Agent(
    model=Gemini(id=model_choice, api_key=os.getenv("GEMINI_API_KEY"), search=True),
    show_tool_calls=True,
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

        # Simulate stream of response
        for chunk in response.content.split():
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.05)  # typing delay

        message_placeholder.markdown(full_response)  # final message

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
