# pip install agno streamlit python-dotenv pyttsx3 edge-tts

import os
import time
import streamlit as st
import pyttsx3
import asyncio
import edge_tts
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from textwrap import dedent

load_dotenv()

# ----------------------------
# 🔊 Ultra-fast Local TTS (Female Voice)
# ----------------------------
def fast_local_tts(text, rate=200):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    voices = engine.getProperty('voices')

    # Select a female voice (Windows: Zira)
    female_voice = None
    for v in voices:
        if "female" in v.name.lower() or "zira" in v.name.lower():
            female_voice = v
            break
    if female_voice:
        engine.setProperty('voice', female_voice.id)
    else:
        engine.setProperty('voice', voices[0].id)

    engine.say(text)
    engine.runAndWait()

# ----------------------------
# 🎤 Microsoft Edge TTS (Optional, higher quality)
# ----------------------------
async def fast_edge_tts(text, voice="en-US-JessaNeural", file_name="output.wav"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_name)
    return file_name

def edge_tts_sync(text, voice="en-US-JessaNeural", file_name="output.wav"):
    asyncio.run(fast_edge_tts(text, voice, file_name))
    return file_name


# ----------------------------
# 🌐 Streamlit UI setup
# ----------------------------
st.set_page_config(page_title="Agno", page_icon="👾", layout="centered")
st.markdown(
    "<h1><span style='color: #fc4503;'> 👻 Agno </span><span style='color: #0313fc;'>Gemini</span> Chatbot<img src='https://logos-world.net/wp-content/uploads/2025/01/Bard-Logo-2023.png' width='70'></h1>",
    unsafe_allow_html=True,
)

# Sidebar - Model selection
st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose Gemini Model",
    ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
    index=0
)

# Choose TTS type
tts_choice = st.sidebar.radio("Choose TTS Engine", ["Local (pyttsx3 - Female)", "Edge (Jessa Neural)"], index=0)

# Initialize agent
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

        # Simulate streaming typing
        for chunk in response.content.split():
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.05)

        message_placeholder.markdown(full_response)

        # 🔊 Speak the response (Female Voice)
        if tts_choice == "Local (pyttsx3 - Female)":
            fast_local_tts(full_response)
        else:
            wav_file = edge_tts_sync(full_response, voice="en-US-JessaNeural")
            st.audio(wav_file, format="audio/wav")

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
